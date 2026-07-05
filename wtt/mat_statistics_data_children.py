"""Statistische Auswertung der 11 Messvariablen unterhalb von Data.

Erwartete MAT-Struktur (vereinfacht):

Data
├── Tower
├── RotorSpeed
├── ...
└── weitere Messvariablen

Für jede Testdatei wird für jedes direkte Unterfeld von Data genau eine
Statistikzeile erzeugt. Alle numerischen Werte innerhalb dieses Unterfelds
werden rekursiv berücksichtigt, unabhängig davon, ob sie als Zeilenvektor,
Spaltenvektor, Matrix, MATLAB-Struct oder Cell-Array gespeichert sind.

Ausgabe:
wind-tunnel-testing/mat_auswertung/mat_summary.csv
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import loadmat


def is_mat_struct(value: Any) -> bool:
    """Erkennt MATLAB-Structs, die von scipy.io.loadmat erzeugt werden."""
    return hasattr(value, "_fieldnames") and value._fieldnames is not None


def unwrap_singleton(value: Any) -> Any:
    """Entpackt Arrays/Objektarrays mit genau einem Element."""
    current = value

    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.flat[0]

    return current


def collect_numeric_values(value: Any) -> list[float]:
    """Sammelt rekursiv alle numerischen Werte eines Variablenordners."""
    value = unwrap_singleton(value)

    if value is None:
        return []

    if is_mat_struct(value):
        result: list[float] = []

        for field_name in value._fieldnames:
            field_value = getattr(value, field_name)
            result.extend(collect_numeric_values(field_value))

        return result

    array = np.asarray(value)

    if array.size == 0:
        return []

    if array.dtype == object:
        result: list[float] = []

        for item in array.ravel(order="C"):
            result.extend(collect_numeric_values(item))

        return result

    if array.dtype.names:
        result: list[float] = []

        for field_name in array.dtype.names:
            result.extend(collect_numeric_values(array[field_name]))

        return result

    if np.issubdtype(array.dtype, np.number) or np.issubdtype(
        array.dtype,
        np.bool_,
    ):
        return [
            float(item)
            for item in array.astype(float, copy=False).ravel(order="C")
        ]

    # Text, Dateinamen, Labels usw. sind keine Messwerte.
    return []


def safe_stat(values: np.ndarray, function: Any) -> float:
    """Berechnet Statistik oder NaN, wenn keine gültigen Werte vorhanden sind."""
    finite_values = values[np.isfinite(values)]

    if finite_values.size == 0:
        return math.nan

    return float(function(finite_values))


def calculate_statistics(values_list: list[float]) -> dict[str, float | int]:
    """Berechnet Mittelwert, Median, Standardabweichung, Min, Max und RMS."""
    values = np.asarray(values_list, dtype=float)
    finite_values = values[np.isfinite(values)]

    if finite_values.size == 0:
        rms = math.nan
    else:
        rms = float(np.sqrt(np.mean(np.square(finite_values))))

    return {
        "Mittelwert": safe_stat(values, np.mean),
        "Median": safe_stat(values, np.median),
        "Standardabweichung": safe_stat(
            values,
            lambda x: np.std(x, ddof=0),
        ),
        "Minimalwert": safe_stat(values, np.min),
        "Maximalwert": safe_stat(values, np.max),
        "RMS": rms,
        "Anzahl_Werte": int(finite_values.size),
    }


def extract_test_number(file_name: str) -> int | float:
    """Extrahiert möglichst robust die Testnummer aus dem Dateinamen."""
    stem = Path(file_name).stem

    match = re.search(
        r"(?i)\btest[\s_\-]*0*(\d{1,3})\b",
        stem,
    )
    if match:
        return int(match.group(1))

    numbers = re.findall(r"\d+", stem)
    if numbers:
        return int(numbers[-1])

    return math.nan


def get_data_variable(mat_data: dict[str, Any], mat_path: Path) -> Any:
    """Liest die MATLAB-Hauptvariable Data und entpackt Einzelelement-Arrays."""
    if "Data" not in mat_data:
        available = [
            key
            for key in mat_data
            if not key.startswith("__")
        ]
        raise KeyError(
            f"In {mat_path.name} wurde keine Variable 'Data' gefunden. "
            f"Gefunden wurden: {available}"
        )

    return unwrap_singleton(mat_data["Data"])


def direct_children_of_data(data: Any) -> list[tuple[str, Any]]:
    """Gibt die direkten Unterfelder von Data zurück.

    Genau diese Felder sind die gesuchten Messvariablen, z. B. Tower.
    """
    data = unwrap_singleton(data)

    if is_mat_struct(data):
        return [
            (field_name, getattr(data, field_name))
            for field_name in data._fieldnames
        ]

    array = np.asarray(data)

    if array.dtype.names:
        return [
            (field_name, array[field_name])
            for field_name in array.dtype.names
        ]

    raise TypeError(
        "'Data' ist weder ein MATLAB-Struct noch ein strukturiertes Array."
    )


def analyse_mat_file(mat_path: Path) -> list[dict[str, Any]]:
    """Erzeugt pro direktem Unterfeld von Data genau eine Statistikzeile."""
    mat_data = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False,
    )

    test_number = extract_test_number(mat_path.name)
    data = get_data_variable(mat_data, mat_path)
    variables = direct_children_of_data(data)

    rows: list[dict[str, Any]] = []

    for variable_name, variable_value in variables:
        values = collect_numeric_values(variable_value)
        statistics = calculate_statistics(values)

        rows.append(
            {
                "Test": test_number,
                "Datei": mat_path.name,
                "Variable": variable_name,
                **statistics,
            }
        )

    return rows


def write_summary_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Schreibt alle Test-/Variablenstatistiken in eine CSV-Datei."""
    columns = [
        "Test",
        "Datei",
        "Variable",
        "Mittelwert",
        "Median",
        "Standardabweichung",
        "Minimalwert",
        "Maximalwert",
        "RMS",
        "Anzahl_Werte",
    ]

    def sort_key(row: dict[str, Any]) -> tuple[float, str]:
        test = row["Test"]

        try:
            test_value = float(test)
        except (TypeError, ValueError):
            test_value = math.inf

        if math.isnan(test_value):
            test_value = math.inf

        return test_value, str(row["Variable"]).lower()

    rows = sorted(rows, key=sort_key)

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    # Skript liegt in:
    # wind-tunnel-testing/wtt/mat_statistics_data_children.py
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    # data und wtt liegen auf derselben Ebene.
    input_dir = project_root / "data"
    output_dir = project_root / "mat_auswertung"
    output_path = output_dir / "mat_summary.csv"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Ausgeführte Datei: {Path(__file__).resolve()}")
    print(f"Eingabeordner:     {input_dir.resolve()}")
    print(f"Ausgabeordner:     {output_dir.resolve()}")

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Der Datenordner wurde nicht gefunden:\n{input_dir.resolve()}"
        )

    mat_files = sorted(input_dir.rglob("*.mat"))

    if not mat_files:
        raise FileNotFoundError(
            f"Keine .mat-Dateien in {input_dir.resolve()} "
            "oder dessen Unterordnern gefunden."
        )

    print(f"Gefundene MAT-Dateien: {len(mat_files)}")

    all_rows: list[dict[str, Any]] = []

    for mat_path in mat_files:
        try:
            rows = analyse_mat_file(mat_path)
            all_rows.extend(rows)

            print(
                f"{mat_path.name}: "
                f"{len(rows)} direkte Data-Variablen ausgewertet"
            )

        except Exception as error:
            print(
                f"Fehler bei {mat_path.name}: "
                f"{type(error).__name__}: {error}"
            )

    if not all_rows:
        raise RuntimeError(
            "Keine Statistikzeilen wurden erzeugt."
        )

    write_summary_csv(
        all_rows,
        output_path,
    )

    print("\nAuswertung abgeschlossen.")
    print(f"Ergebnisdatei:\n{output_path.resolve()}")


if __name__ == "__main__":
    main()
