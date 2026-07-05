"""Statistische Auswertung der Variablen unter Data.ModelsData.Model1.

Sonderstruktur:
- Tower -> FA, SS
- Pitch -> Blade1, Blade1Dem, Blade2, Blade2Dem, Blade3, Blade3Dem
- Hub -> Yawing, Nodding, Torque
- Power Reference -> Rel, Abs

Für diese vier Variablen wird eine Ebene tiefer ausgewertet.
Alle anderen Variablen werden direkt ausgewertet.

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


# Erwartete Untervariablen.
# Die Schlüssel werden intern normalisiert, sodass z. B.
# "Power Reference", "PowerReference" und "Power_Reference" gleich behandelt werden.
NESTED_VARIABLES: dict[str, tuple[str, ...]] = {
    "tower": ("FA", "SS"),
    "pitch": (
        "Blade1",
        "Blade1Dem",
        "Blade2",
        "Blade2Dem",
        "Blade3",
        "Blade3Dem",
    ),
    "hub": ("Yawing", "Nodding", "Torque"),
    "powerreference": ("Rel", "Abs"),
}


def normalize_name(name: str) -> str:
    """Entfernt Leerzeichen/Sonderzeichen und vereinheitlicht Groß-/Kleinschreibung."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def is_mat_struct(value: Any) -> bool:
    """Erkennt MATLAB-Structs von scipy.io.loadmat."""
    return hasattr(value, "_fieldnames") and value._fieldnames is not None


def unwrap_singleton(value: Any) -> Any:
    """Entpackt Arrays mit genau einem Element."""
    current = value

    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.flat[0]

    return current


def get_struct_fields(structure: Any) -> dict[str, Any]:
    """Gibt die direkten Felder einer MATLAB-Struktur als Dictionary zurück."""
    structure = unwrap_singleton(structure)

    if is_mat_struct(structure):
        return {
            field_name: getattr(structure, field_name)
            for field_name in structure._fieldnames
        }

    array = np.asarray(structure)

    if array.dtype.names:
        return {
            field_name: array[field_name]
            for field_name in array.dtype.names
        }

    return {}


def get_struct_field(structure: Any, field_name: str) -> Any:
    """Liest ein Feld robust und unabhängig von Schreibweise/Unterstrichen."""
    fields = get_struct_fields(structure)

    target = normalize_name(field_name)

    for existing_name, value in fields.items():
        if normalize_name(existing_name) == target:
            return unwrap_singleton(value)

    raise KeyError(
        f"Feld '{field_name}' nicht gefunden. "
        f"Vorhanden: {list(fields.keys())}"
    )


def collect_numeric_values(value: Any) -> list[float]:
    """Sammelt rekursiv alle numerischen Werte."""
    value = unwrap_singleton(value)

    if value is None:
        return []

    if is_mat_struct(value):
        result: list[float] = []

        for field_name in value._fieldnames:
            result.extend(
                collect_numeric_values(getattr(value, field_name))
            )

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
            result.extend(
                collect_numeric_values(array[field_name])
            )

        return result

    if np.issubdtype(array.dtype, np.number) or np.issubdtype(
        array.dtype,
        np.bool_,
    ):
        return [
            float(item)
            for item in array.astype(float, copy=False).ravel(order="C")
        ]

    # Text und Labels werden nicht als Messwerte verwendet.
    return []


def safe_stat(values: np.ndarray, function: Any) -> float:
    """Berechnet eine Statistik oder NaN bei leeren Daten."""
    finite_values = values[np.isfinite(values)]

    if finite_values.size == 0:
        return math.nan

    return float(function(finite_values))


def calculate_statistics(values_list: list[float]) -> dict[str, float | int]:
    """Berechnet Mittelwert, Median, Standardabweichung, Min, Max und RMS."""
    values = np.asarray(values_list, dtype=float)
    finite_values = values[np.isfinite(values)]

    rms = (
        float(np.sqrt(np.mean(np.square(finite_values))))
        if finite_values.size > 0
        else math.nan
    )

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
    """Extrahiert die Testnummer aus dem Dateinamen."""
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


def make_row(
    test_number: int | float,
    file_name: str,
    variable_name: str,
    values: list[float],
) -> dict[str, Any]:
    """Erzeugt eine vollständige Ergebniszeile."""
    return {
        "Test": test_number,
        "Datei": file_name,
        "Variable": variable_name,
        **calculate_statistics(values),
    }


def analyse_mat_file(mat_path: Path) -> list[dict[str, Any]]:
    """Öffnet Data -> ModelsData -> Model1 und wertet die gewünschte Ebene aus."""
    mat_data = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False,
    )

    if "Data" not in mat_data:
        available = [
            key
            for key in mat_data
            if not key.startswith("__")
        ]
        raise KeyError(
            f"In {mat_path.name} wurde 'Data' nicht gefunden. "
            f"Vorhanden: {available}"
        )

    data = unwrap_singleton(mat_data["Data"])
    models_data = get_struct_field(data, "ModelsData")
    model1 = get_struct_field(models_data, "Model1")

    model1_fields = get_struct_fields(model1)
    test_number = extract_test_number(mat_path.name)

    rows: list[dict[str, Any]] = []

    for variable_name, variable_value in model1_fields.items():
        normalized_variable = normalize_name(variable_name)

        # Für diese Variablen eine Ebene tiefer auswerten.
        if normalized_variable in NESTED_VARIABLES:
            child_fields = get_struct_fields(variable_value)

            for expected_child in NESTED_VARIABLES[normalized_variable]:
                matching_child_name = None
                matching_child_value = None

                for existing_child_name, existing_child_value in child_fields.items():
                    if normalize_name(existing_child_name) == normalize_name(expected_child):
                        matching_child_name = existing_child_name
                        matching_child_value = existing_child_value
                        break

                output_name = (
                    f"{variable_name}.{matching_child_name}"
                    if matching_child_name is not None
                    else f"{variable_name}.{expected_child}"
                )

                # Fehlt ein erwartetes Feld, wird eine NaN-Zeile erzeugt.
                values = (
                    collect_numeric_values(matching_child_value)
                    if matching_child_name is not None
                    else []
                )

                rows.append(
                    make_row(
                        test_number=test_number,
                        file_name=mat_path.name,
                        variable_name=output_name,
                        values=values,
                    )
                )

        # Alle anderen Variablen direkt auswerten.
        else:
            rows.append(
                make_row(
                    test_number=test_number,
                    file_name=mat_path.name,
                    variable_name=variable_name,
                    values=collect_numeric_values(variable_value),
                )
            )

    return rows


def write_summary_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Schreibt alle Ergebnisse in eine CSV-Datei."""
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
        try:
            test_value = float(row["Test"])
        except (TypeError, ValueError):
            test_value = math.inf

        if math.isnan(test_value):
            test_value = math.inf

        return test_value, str(row["Variable"]).lower()

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
        writer.writerows(sorted(rows, key=sort_key))


def main() -> None:
    # Skript liegt in wind-tunnel-testing/wtt/
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    input_dir = project_root / "data"
    output_dir = project_root / "mat_auswertung"
    output_path = output_dir / "mat_summary.csv"

    output_dir.mkdir(parents=True, exist_ok=True)

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
            f"Keine .mat-Dateien in {input_dir.resolve()} gefunden."
        )

    print(f"Gefundene MAT-Dateien: {len(mat_files)}")

    all_rows: list[dict[str, Any]] = []

    for mat_path in mat_files:
        try:
            rows = analyse_mat_file(mat_path)
            all_rows.extend(rows)

            print(
                f"{mat_path.name}: "
                f"{len(rows)} Statistikzeilen erzeugt"
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

    write_summary_csv(all_rows, output_path)

    print("\nAuswertung abgeschlossen.")
    print(f"Ergebnisdatei:\n{output_path.resolve()}")


if __name__ == "__main__":
    main()
