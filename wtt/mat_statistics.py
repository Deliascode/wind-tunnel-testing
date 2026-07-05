"""MAT-Dateien rekursiv auslesen und Statistiken je Messvariable erzeugen.

Ausgabe:
- mat_summary.csv:
    Datei, Variable, Mittelwert, Median, Standardabweichung,
    Minimalwert, Maximalwert, RMS, Anzahl_Werte
- Pro MAT-Datei eine JSON-Datei mit denselben Statistiken und allen Einzelwerten.

Leere Felder und nichtnumerische Werte werden als NaN ausgegeben.
Zeilen- und Spaltenvektoren werden gleich behandelt.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from scipy.io import loadmat


def is_mat_struct(value: Any) -> bool:
    """Erkennt MATLAB-Strukturen, die scipy.io.loadmat erzeugt."""
    return hasattr(value, "_fieldnames") and value._fieldnames is not None


def walk_variables(value: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Durchläuft verschachtelte MATLAB-Strukturen rekursiv."""
    if is_mat_struct(value):
        for field_name in value._fieldnames:
            child = getattr(value, field_name)
            child_name = f"{prefix}.{field_name}" if prefix else field_name
            yield from walk_variables(child, child_name)
        return

    # Objekt-Arrays können weitere MATLAB-Strukturen enthalten.
    array = np.asarray(value)
    if array.dtype == object:
        for index, item in enumerate(array.ravel(order="C")):
            item_name = f"{prefix}[{index}]"
            yield from walk_variables(item, item_name)
        return

    yield prefix, value


def to_numeric_values(value: Any) -> np.ndarray:
    """Wandelt Zeilen-/Spaltenvektoren und Skalare in einen 1-D-float-Array um."""
    if value is None:
        return np.array([np.nan], dtype=float)

    array = np.asarray(value)

    # Wichtig: Sowohl Daten in der ersten Zeile als auch in der ersten Spalte
    # werden zu derselben eindimensionalen Reihenfolge abgeflacht.
    array = array.ravel(order="C")

    if array.size == 0:
        return np.array([np.nan], dtype=float)

    numeric_values: list[float] = []
    for item in array:
        try:
            if item is None or (isinstance(item, str) and not item.strip()):
                numeric_values.append(np.nan)
            else:
                numeric_values.append(float(item))
        except (TypeError, ValueError):
            numeric_values.append(np.nan)

    return np.asarray(numeric_values, dtype=float)


def safe_statistic(function: Any, values: np.ndarray) -> float:
    """Berechnet eine Statistik; bei vollständig leeren Daten wird NaN geliefert."""
    finite_values = values[np.isfinite(values)]
    if finite_values.size == 0:
        return math.nan
    return float(function(finite_values))


def calculate_statistics(variable_name: str, raw_value: Any) -> dict[str, Any]:
    """Erzeugt alle gewünschten Kennwerte und die Einzelwerte."""
    values = to_numeric_values(raw_value)
    finite_values = values[np.isfinite(values)]

    rms = (
        float(np.sqrt(np.mean(np.square(finite_values))))
        if finite_values.size
        else math.nan
    )

    return {
        "Variable": variable_name,
        "Mittelwert": safe_statistic(np.mean, values),
        "Median": safe_statistic(np.median, values),
        "Standardabweichung": safe_statistic(np.std, values),
        "Minimalwert": safe_statistic(np.min, values),
        "Maximalwert": safe_statistic(np.max, values),
        "RMS": rms,
        "Anzahl_Werte": int(values.size),
        # NaN bleibt in Python/JSON ausdrücklich als NaN erhalten.
        "Werte": [float(item) if np.isfinite(item) else math.nan for item in values],
    }


def analyse_mat_file(mat_path: Path) -> list[dict[str, Any]]:
    """Liest eine MAT-Datei und analysiert alle numerischen Endvariablen."""
    mat_data = loadmat(mat_path, squeeze_me=False, struct_as_record=False)

    results: list[dict[str, Any]] = []

    for top_level_name, top_level_value in mat_data.items():
        if top_level_name.startswith("__"):
            continue

        for variable_name, raw_value in walk_variables(
            top_level_value, top_level_name
        ):
            results.append(calculate_statistics(variable_name, raw_value))

    return results


def write_json(mat_path: Path, results: list[dict[str, Any]], output_dir: Path) -> None:
    """Speichert Statistiken und alle Einzelwerte einer MAT-Datei."""
    output_path = output_dir / f"{mat_path.stem}_statistics.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "Datei": mat_path.name,
                "Variablen": results,
            },
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=True,
        )


def write_summary_csv(
    all_results: list[tuple[Path, list[dict[str, Any]]]],
    output_dir: Path,
) -> None:
    """Schreibt eine kompakte, kombinierte Statistik-Tabelle."""
    output_path = output_dir / "mat_summary.csv"
    columns = [
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

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
        writer.writeheader()

        for mat_path, results in all_results:
            for result in results:
                writer.writerow(
                    {
                        "Datei": mat_path.name,
                        **{column: result[column] for column in columns[1:]},
                    }
                )


def main() -> None:
    input_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir = Path("mat_auswertung")
    output_dir.mkdir(parents=True, exist_ok=True)

    mat_files = sorted(input_dir.glob("*.mat"))
    if not mat_files:
        raise FileNotFoundError(
            f"Keine .mat-Dateien in {input_dir.resolve()} gefunden."
        )

    all_results: list[tuple[Path, list[dict[str, Any]]]] = []

    for mat_path in mat_files:
        results = analyse_mat_file(mat_path)
        write_json(mat_path, results, output_dir)
        all_results.append((mat_path, results))
        print(f"Ausgewertet: {mat_path.name} ({len(results)} Variablen)")

    write_summary_csv(all_results, output_dir)
    print(f"\nAusgabe gespeichert in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
