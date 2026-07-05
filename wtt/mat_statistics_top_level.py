"""Statistische Auswertung von MAT-Testdateien.

Erwartete Struktur:
wind-tunnel-testing/
├── data/
│   ├── ...Test 1....mat
│   ├── ...Test 2....mat
│   └── ...
└── wtt/
    └── mat_statistics.py

Für jede MAT-Datei (Test 1 bis 31) wird für jede Top-Level-Variable
(z. B. Tower, RotorSpeed usw.) genau eine Statistikzeile erzeugt.

Alle numerischen Daten in den Unterfeldern/Unterordnern einer Variable
werden berücksichtigt. Zeilen- und Spaltenvektoren werden gleich behandelt.

Ausgabe:
mat_auswertung/mat_summary.csv

Spalten:
Test, Datei, Variable, Mittelwert, Median, Standardabweichung,
Minimalwert, Maximalwert, RMS, Anzahl_Werte

Leere oder nichtnumerische Variablen werden mit NaN ausgegeben.
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
    """Prüft, ob ein Objekt eine MATLAB-Struktur ist."""
    return hasattr(value, "_fieldnames") and value._fieldnames is not None


def collect_numeric_values(value: Any) -> list[float]:
    """Sammelt rekursiv alle numerischen Werte aus einer MATLAB-Variable.

    Berücksichtigt:
    - Skalare
    - Zeilenvektoren
    - Spaltenvektoren
    - Matrizen
    - verschachtelte MATLAB-Strukturen
    - Objekt-Arrays / Cell-Arrays
    - leere Felder

    Nichtnumerische Inhalte werden ignoriert.
    """
    values: list[float] = []

    if value is None:
        return values

    if is_mat_struct(value):
        for field_name in value._fieldnames:
            child = getattr(value, field_name)
            values.extend(collect_numeric_values(child))
        return values

    array = np.asarray(value)

    if array.size == 0:
        return values

    # Cell-Arrays oder Objekt-Arrays rekursiv durchsuchen.
    if array.dtype == object:
        for item in array.ravel(order="C"):
            values.extend(collect_numeric_values(item))
        return values

    # Strukturierte NumPy-Arrays ebenfalls rekursiv durchsuchen.
    if array.dtype.names:
        for field_name in array.dtype.names:
            values.extend(collect_numeric_values(array[field_name]))
        return values

    # Boolesche und numerische Arrays übernehmen.
    if np.issubdtype(array.dtype, np.number) or np.issubdtype(array.dtype, np.bool_):
        flat = array.astype(float, copy=False).ravel(order="C")
        values.extend(float(item) for item in flat)
        return values

    # Zeichenketten und andere Datentypen werden nicht als Messwerte verwendet.
    return values


def nan_if_empty(values: np.ndarray, function: Any) -> float:
    """Berechnet eine Statistik oder liefert NaN bei fehlenden Werten."""
    finite_values = values[np.isfinite(values)]

    if finite_values.size == 0:
        return math.nan

    return float(function(finite_values))


def calculate_statistics(values_list: list[float]) -> dict[str, float | int]:
    """Berechnet alle geforderten Statistiken."""
    if not values_list:
        values = np.array([], dtype=float)
    else:
        values = np.asarray(values_list, dtype=float)

    finite_values = values[np.isfinite(values)]

    if finite_values.size == 0:
        rms = math.nan
    else:
        rms = float(np.sqrt(np.mean(np.square(finite_values))))

    return {
        "Mittelwert": nan_if_empty(values, np.mean),
        "Median": nan_if_empty(values, np.median),
        # ddof=0: Standardabweichung der vollständigen vorhandenen Messreihe
        "Standardabweichung": nan_if_empty(
            values,
            lambda x: np.std(x, ddof=0),
        ),
        "Minimalwert": nan_if_empty(values, np.min),
        "Maximalwert": nan_if_empty(values, np.max),
        "RMS": rms,
        "Anzahl_Werte": int(finite_values.size),
    }


def extract_test_number(file_name: str) -> int | float:
    """Liest die Testnummer aus dem Dateinamen.

    Bevorzugt Muster wie:
    Test_1, Test 1, Test-1, test01

    Falls kein Test-Muster gefunden wird, wird die letzte Zahl
    im Dateinamen verwendet. Falls gar keine Zahl vorkommt: NaN.
    """
    stem = Path(file_name).stem

    test_match = re.search(
        r"(?i)\btest[\s_\-]*0*(\d{1,3})\b",
        stem,
    )

    if test_match:
        return int(test_match.group(1))

    all_numbers = re.findall(r"\d+", stem)

    if all_numbers:
        return int(all_numbers[-1])

    return math.nan


def analyse_mat_file(mat_path: Path) -> list[dict[str, Any]]:
    """Erzeugt pro Top-Level-Variable genau eine Statistikzeile."""
    mat_data = loadmat(
        mat_path,
        squeeze_me=False,
        struct_as_record=False,
    )

    test_number = extract_test_number(mat_path.name)
    rows: list[dict[str, Any]] = []

    for variable_name, variable_value in mat_data.items():
        # Interne MATLAB-Metadaten überspringen.
        if variable_name.startswith("__"):
            continue

        all_values = collect_numeric_values(variable_value)
        statistics = calculate_statistics(all_values)

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
    """Schreibt alle Tests und Variablen in eine gemeinsame CSV-Datei."""
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
        numeric_test = float(test) if isinstance(test, (int, float)) else math.inf
        if math.isnan(numeric_test):
            numeric_test = math.inf
        return numeric_test, str(row["Variable"]).lower()

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
    # Das Skript liegt in wind-tunnel-testing/wtt/
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    # data/ liegt auf derselben Ebene wie wtt/
    input_dir = project_root / "data"
    output_dir = project_root / "mat_auswertung"
    output_path = output_dir / "mat_summary.csv"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Ausgeführte Datei: {Path(__file__).resolve()}")
    print(f"Eingabeordner:     {input_dir.resolve()}")
    print(f"Ausgabeordner:     {output_dir.resolve()}")

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Der Datenordner existiert nicht:\n{input_dir.resolve()}"
        )

    # Durchsucht data/ und alle Unterordner.
    mat_files = sorted(input_dir.rglob("*.mat"))

    if not mat_files:
        raise FileNotFoundError(
            f"Keine .mat-Dateien in {input_dir.resolve()} "
            "oder dessen Unterordnern gefunden."
        )

    print(f"Gefundene MAT-Dateien: {len(mat_files)}")

    all_rows: list[dict[str, Any]] = []

    for mat_path in mat_files:
        rows = analyse_mat_file(mat_path)
        all_rows.extend(rows)

        print(
            f"{mat_path.name}: "
            f"{len(rows)} Variablen ausgewertet"
        )

    write_summary_csv(all_rows, output_path)

    print("\nAuswertung abgeschlossen.")
    print(f"Ergebnisdatei:\n{output_path.resolve()}")


if __name__ == "__main__":
    main()
