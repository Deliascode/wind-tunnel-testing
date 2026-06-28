from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import loadmat


# Projekt-Hauptordner:
# wind-tunnel-testing/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Nur Dateien in diesem Ordner werden eingelesen.
DATA_FOLDER = PROJECT_ROOT / "data"

# Dieser Ordner wird nicht eingelesen.
EXCLUDED_FOLDER = PROJECT_ROOT / "data_excluded"


def load_single_mat_file(file_path: Path) -> Any:
    """
    Lädt eine einzelne MATLAB-Datei.

    Die MATLAB-Struktur bleibt erhalten.
    Beispiel:
        data.ModelsData.Model1.RotorSpeed
    """

    mat_file = loadmat(
        file_path,
        squeeze_me=True,
        struct_as_record=False,
    )

    if "Data" not in mat_file:
        raise KeyError(
            f"In '{file_path.name}' wurde keine Variable "
            "'Data' gefunden."
        )

    return mat_file["Data"]


def load_all_mat_files(folder: Path) -> dict[str, Any]:
    """
    Lädt alle MAT-Dateien aus dem Datenordner
    und seinen Unterordnern.

    Dateien im Ordner data_excluded werden nicht geladen.
    """

    if not folder.exists():
        raise FileNotFoundError(
            f"Der Datenordner wurde nicht gefunden:\n{folder}"
        )

    mat_files = sorted(folder.rglob("*.mat"))

    if not mat_files:
        raise FileNotFoundError(
            f"Im folgenden Ordner wurden keine MAT-Dateien gefunden:\n"
            f"{folder}"
        )

    all_data: dict[str, Any] = {}

    for file_path in mat_files:
        relative_name = str(file_path.relative_to(folder))

        try:
            data = load_single_mat_file(file_path)
            all_data[relative_name] = data

            print(f"Geladen: {relative_name}")

        except Exception as error:
            print(
                f"Fehler beim Laden von {relative_name}: "
                f"{type(error).__name__}: {error}"
            )

    return all_data


def print_signal_information(
    file_name: str,
    signal_name: str,
    signal: Any,
) -> None:
    """
    Zeigt grundlegende Informationen über ein Messsignal.
    """

    array = np.asarray(signal)

    print(f"\nDatei: {file_name}")
    print(f"Signal: {signal_name}")
    print(f"Datentyp: {array.dtype}")
    print(f"Form: {array.shape}")
    print(f"Anzahl Werte: {array.size}")

    if (
        array.size > 0
        and np.issubdtype(array.dtype, np.number)
    ):
        print(f"Minimum: {np.nanmin(array)}")
        print(f"Maximum: {np.nanmax(array)}")
        print(f"Mittelwert: {np.nanmean(array)}")


def main() -> None:
    """
    Lädt alle MAT-Dateien und zeigt einige Messgrößen an.
    """

    print(f"Datenordner: {DATA_FOLDER}")
    print(f"Ausgeschlossener Ordner: {EXCLUDED_FOLDER}\n")

    all_data = load_all_mat_files(DATA_FOLDER)

    print("\n" + "=" * 70)
    print(f"Insgesamt geladen: {len(all_data)} Dateien")
    print("=" * 70)

    for file_name, data in all_data.items():
        try:
            model = data.ModelsData.Model1

            time = data.Time
            rotor_speed = model.RotorSpeed
            pitot_velocity = model.PitotVelocity

            tower_fa = model.Tower.FA
            tower_ss = model.Tower.SS

            hub_yawing = model.Hub.Yawing
            hub_nodding = model.Hub.Nodding
            hub_torque = model.Hub.Torque

            azimuth = model.Azimuth
            yaw = model.Yaw
            yaw_demanded = model.YawDem

            air_density = model.AirDensity

            test_number = data.TN
            recording_start = data.RecordingStart

            print("\n" + "=" * 70)
            print(f"Datei: {file_name}")
            print(f"Testnummer: {test_number}")
            print(f"Aufzeichnungsbeginn: {recording_start}")

            print_signal_information(
                file_name,
                "RotorSpeed",
                rotor_speed,
            )

            print_signal_information(
                file_name,
                "PitotVelocity",
                pitot_velocity,
            )

            print_signal_information(
                file_name,
                "Tower.FA",
                tower_fa,
            )

            print_signal_information(
                file_name,
                "Tower.SS",
                tower_ss,
            )

            print_signal_information(
                file_name,
                "Hub.Torque",
                hub_torque,
            )

        except AttributeError as error:
            print(
                f"\nStrukturproblem in '{file_name}': {error}"
            )


if __name__ == "__main__":
    main()