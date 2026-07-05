from __future__ import annotations

from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from scipy.io import loadmat

from blockage import blockage_ratio, equivalent_free_air_speed


# =========================
# User settings / constants
# =========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "plots_cp_ct_mean"
TEST_MATRIX_PATH = DATA_DIR / "Task1_Performance_TestMatrix_Group2_measurements.xlsx"

# From the repository / README:
ROTOR_RADIUS_M = 0.5436
ROTOR_AREA_M2 = math.pi * ROTOR_RADIUS_M**2

# Wind-tunnel geometry.
# For blockage, only the cross-sectional area perpendicular to the flow is used.
TUNNEL_WIDTH_M = 2.7
TUNNEL_HEIGHT_M = 1.8
TUNNEL_DEPTH_M = 4.5
TUNNEL_CROSS_SECTION_M2 = TUNNEL_WIDTH_M * TUNNEL_HEIGHT_M
BLOCKAGE_RATIO = blockage_ratio(
    rotor_area=ROTOR_AREA_M2,
    tunnel_area=TUNNEL_CROSS_SECTION_M2,
)

# Hub.Torque in the MAT files appears to be in mNm for the uploaded examples.
# Therefore convert to Nm:
TORQUE_SCALE_TO_NM = 1e-3

# IMPORTANT:
# To compute cT from Tower.FA you need a lever arm / calibration distance.
# Replace this with the correct distance from your setup if necessary.
# Example assumption:
THRUST_LEVER_ARM_M = 0.72


# =========================
# Helper functions
# =========================

def unwrap_singleton(value):
    current = value
    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.flat[0]
    return current


def load_model1(mat_path: Path):
    mat_data = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    data = unwrap_singleton(mat_data["Data"])
    models_data = unwrap_singleton(data.ModelsData)
    model1 = unwrap_singleton(models_data.Model1)
    return model1


MEASUREMENT_DURATION_S = 8.0


def resample_to_common_time(
    values: np.ndarray,
    target_length: int,
    duration_s: float = MEASUREMENT_DURATION_S,
) -> np.ndarray:
    """cP- und cT-Auswertung mit arithmetischen Mittelwerten.

Die Datenstruktur, Interpolation, Blockage-Korrektur und Ordnerstruktur
entsprechen dem vorherigen Skript. Für jede Yaw-Situation werden Mittelwert,
Mittelwert ± Standardabweichung, Minimum und Maximum dargestellt.

Interpoliert ein Signal über den gemeinsamen Messzeitraum.

    Alle Messungen dauern gleich lang. Deshalb wird für jedes Signal eine
    Zeitachse von 0 bis duration_s erzeugt und anschließend auf die gemeinsame
    Zielzeitachse interpoliert.
    """

    values = np.asarray(values, dtype=float).ravel(order="C")

    if target_length <= 0:
        raise ValueError("target_length muss größer als 0 sein.")

    if values.size == 0:
        return np.full(target_length, np.nan, dtype=float)

    if values.size == 1:
        return np.full(target_length, values[0], dtype=float)

    if values.size == target_length:
        return values.astype(float, copy=False)

    finite_mask = np.isfinite(values)

    if finite_mask.sum() == 0:
        return np.full(target_length, np.nan, dtype=float)

    if finite_mask.sum() == 1:
        return np.full(
            target_length,
            values[finite_mask][0],
            dtype=float,
        )

    source_time = np.linspace(
        0.0,
        duration_s,
        values.size,
        endpoint=True,
    )
    target_time = np.linspace(
        0.0,
        duration_s,
        target_length,
        endpoint=True,
    )

    return np.interp(
        target_time,
        source_time[finite_mask],
        values[finite_mask],
    )


def get_array(value) -> np.ndarray:
    array = np.asarray(unwrap_singleton(value), dtype=float).ravel(order="C")
    if array.size == 0:
        return np.array([np.nan], dtype=float)
    return array


def finite_only(*arrays):
    """Return arrays filtered to indices where all arrays are finite."""
    stacked = [np.asarray(a, dtype=float).ravel(order="C") for a in arrays]
    min_len = min(len(a) for a in stacked)
    stacked = [a[:min_len] for a in stacked]
    mask = np.ones(min_len, dtype=bool)
    for a in stacked:
        mask &= np.isfinite(a)
    return [a[mask] for a in stacked]


def safe_stat(values: np.ndarray, fn):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return math.nan
    return float(fn(values))


def compute_test_statistics(mat_path: Path) -> dict:
    """Berechnet TSR, cP und cT mit Glauert-Blockage-Korrektur.

    Ablauf:
    1. Alle Signale werden über die gemeinsamen 8 Sekunden interpoliert.
    2. Aus PitotVelocity und Tower.FA wird zunächst der unkorregierte cT berechnet.
    3. blockage.py berechnet daraus für jeden Zeitpunkt U'_inf.
    4. TSR, cP und der korrigierte cT werden mit U'_inf berechnet.
    """

    model1 = load_model1(mat_path)

    rotor_speed_rpm = get_array(model1.RotorSpeed)
    pitot_velocity = get_array(model1.PitotVelocity)
    air_density = get_array(model1.AirDensity)
    hub_torque_raw = get_array(model1.Hub.Torque)
    tower_fa_moment = get_array(model1.Tower.FA)
    yaw_actual = get_array(model1.Yaw)

    common_length = max(
        rotor_speed_rpm.size,
        pitot_velocity.size,
        air_density.size,
        hub_torque_raw.size,
        tower_fa_moment.size,
        yaw_actual.size,
    )

    rotor_speed_common = resample_to_common_time(
        rotor_speed_rpm,
        common_length,
    )
    pitot_velocity_common = resample_to_common_time(
        pitot_velocity,
        common_length,
    )
    air_density_common = resample_to_common_time(
        air_density,
        common_length,
    )
    torque_common_raw = resample_to_common_time(
        hub_torque_raw,
        common_length,
    )
    tower_fa_common = resample_to_common_time(
        tower_fa_moment,
        common_length,
    )
    yaw_common = resample_to_common_time(
        yaw_actual,
        common_length,
    )

    omega = (
        rotor_speed_common
        * 2.0
        * math.pi
        / 60.0
    )

    torque_nm = torque_common_raw * TORQUE_SCALE_TO_NM
    power_w = torque_nm * omega

    # Tower.FA is a tower-base bending moment.
    # Convert it to rotor thrust using the 0.72 m force arm.
    thrust_n = -tower_fa_common / THRUST_LEVER_ARM_M

    # ------------------------------------------------------------
    # 1) Uncorrected thrust coefficient based on PitotVelocity U_inf
    # ------------------------------------------------------------
    ct_uncorrected_denominator = (
        0.5
        * air_density_common
        * ROTOR_AREA_M2
        * pitot_velocity_common**2
    )

    ct_uncorrected = np.divide(
        thrust_n,
        ct_uncorrected_denominator,
        out=np.full(common_length, np.nan),
        where=(
            np.isfinite(ct_uncorrected_denominator)
            & (ct_uncorrected_denominator != 0.0)
        ),
    )

    # Glauert contains CT / (1 - CT). Values >= 1 are not valid for this
    # simple correction and are therefore excluded.
    valid_glauert = (
        np.isfinite(pitot_velocity_common)
        & np.isfinite(ct_uncorrected)
        & (pitot_velocity_common > 0.0)
        & (ct_uncorrected < 1.0)
    )

    free_air_velocity = np.full(common_length, np.nan)

    free_air_velocity[valid_glauert] = equivalent_free_air_speed(
        commanded_tunnel_speed_value=pitot_velocity_common[valid_glauert],
        thrust_coefficient=ct_uncorrected[valid_glauert],
        blockage_ratio_value=BLOCKAGE_RATIO,
    )

    # ------------------------------------------------------------
    # 2) Corrected TSR, cP and cT based on equivalent free-air speed
    # ------------------------------------------------------------
    tsr_series = np.divide(
        omega * ROTOR_RADIUS_M,
        free_air_velocity,
        out=np.full(common_length, np.nan),
        where=(
            np.isfinite(free_air_velocity)
            & (free_air_velocity != 0.0)
        ),
    )

    cp_denominator = (
        0.5
        * air_density_common
        * ROTOR_AREA_M2
        * free_air_velocity**3
    )

    cp_series = np.divide(
        power_w,
        cp_denominator,
        out=np.full(common_length, np.nan),
        where=(
            np.isfinite(cp_denominator)
            & (cp_denominator != 0.0)
        ),
    )

    ct_corrected_denominator = (
        0.5
        * air_density_common
        * ROTOR_AREA_M2
        * free_air_velocity**2
    )

    ct_series = np.divide(
        thrust_n,
        ct_corrected_denominator,
        out=np.full(common_length, np.nan),
        where=(
            np.isfinite(ct_corrected_denominator)
            & (ct_corrected_denominator != 0.0)
        ),
    )

    return {
        "yaw_actual_mean": safe_stat(yaw_common, np.mean),
        "pitot_velocity_mean": safe_stat(
            pitot_velocity_common,
            np.mean,
        ),
        "free_air_velocity_mean": safe_stat(
            free_air_velocity,
            np.mean,
        ),
        "ct_uncorrected_mean": safe_stat(
            ct_uncorrected,
            np.mean,
        ),
        "tsr_mean": safe_stat(tsr_series, np.median),
        "tsr_std": safe_stat(tsr_series, np.std),
        "cp_mean": safe_stat(cp_series, np.mean),
        "cp_std": safe_stat(cp_series, np.std),
        "cp_min": safe_stat(cp_series, np.min),
        "cp_max": safe_stat(cp_series, np.max),
        "ct_mean": safe_stat(ct_series, np.mean),
        "ct_std": safe_stat(ct_series, np.std),
        "ct_min": safe_stat(ct_series, np.min),
        "ct_max": safe_stat(ct_series, np.max),
    }

def load_test_matrix(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Task1 Performance G2"]

    headers = [ws.cell(row=1, column=i).value for i in range(1, 31)]

    records = []
    for row_idx in range(2, ws.max_row + 1):
        test_number = ws.cell(row=row_idx, column=1).value
        if test_number is None:
            continue

        record = {}
        for col_idx, header in enumerate(headers, start=1):
            record[header] = ws.cell(row=row_idx, column=col_idx).value
        records.append(record)

    return records


def build_dataframe_like_records() -> list[dict]:
    records = load_test_matrix(TEST_MATRIX_PATH)
    rows = []

    for record in records:
        top = record["Top"]
        file_number = record["File number"]

        if top is None or file_number is None:
            continue

        mat_name = f"Results_File_{int(file_number)}_TOP_{int(top)}.mat"
        mat_path = DATA_DIR / mat_name

        if not mat_path.exists():
            print(f"Datei fehlt, übersprungen: {mat_name}")
            continue

        stats = compute_test_statistics(mat_path)

        rows.append(
            {
                "test": record["Test number"],
                "yaw_target": record["Yaw [deg]"],
                "yaw_actual_mean": stats["yaw_actual_mean"],
                "pitot_velocity_mean": stats["pitot_velocity_mean"],
                "free_air_velocity_mean": stats["free_air_velocity_mean"],
                "ct_uncorrected_mean": stats["ct_uncorrected_mean"],
                "tsr_expected": record["TSR [-]"],
                "tsr_mean": stats["tsr_mean"],
                "tsr_std": stats["tsr_std"],
                "cp_mean": stats["cp_mean"],
                "cp_plus_std": (
                    stats["cp_mean"] + stats["cp_std"]
                    if np.isfinite(stats["cp_mean"]) and np.isfinite(stats["cp_std"])
                    else math.nan
                ),
                "cp_minus_std": (
                    stats["cp_mean"] - stats["cp_std"]
                    if np.isfinite(stats["cp_mean"]) and np.isfinite(stats["cp_std"])
                    else math.nan
                ),
                "cp_min": stats["cp_min"],
                "cp_max": stats["cp_max"],
                "ct_mean": stats["ct_mean"],
                "ct_plus_std": (
                    stats["ct_mean"] + stats["ct_std"]
                    if np.isfinite(stats["ct_mean"]) and np.isfinite(stats["ct_std"])
                    else math.nan
                ),
                "ct_minus_std": (
                    stats["ct_mean"] - stats["ct_std"]
                    if np.isfinite(stats["ct_mean"]) and np.isfinite(stats["ct_std"])
                    else math.nan
                ),
                "ct_min": stats["ct_min"],
                "ct_max": stats["ct_max"],
                "mat_file": mat_name,
            }
        )

    return rows


def plot_for_yaw(rows: list[dict], yaw_value: float, coefficient_prefix: str):
    """
    coefficient_prefix: 'cp' or 'ct'
    Produces one plot with:
    median, median+std, median-std, min, max
    """
    yaw_rows = [r for r in rows if r["yaw_target"] == yaw_value]
    yaw_rows.sort(key=lambda r: (r["tsr_mean"] if r["tsr_mean"] is not None else math.inf))

    x = [r["tsr_mean"] for r in yaw_rows]
    y_mean = [r[f"{coefficient_prefix}_mean"] for r in yaw_rows]
    y_plus_std = [r[f"{coefficient_prefix}_plus_std"] for r in yaw_rows]
    y_minus_std = [r[f"{coefficient_prefix}_minus_std"] for r in yaw_rows]
    y_min = [r[f"{coefficient_prefix}_min"] for r in yaw_rows]
    y_max = [r[f"{coefficient_prefix}_max"] for r in yaw_rows]

    coeff_label = "cP" if coefficient_prefix == "cp" else "cT"

    plt.figure(figsize=(10, 6))
    plt.plot(x, y_mean, marker="o", label="Mittelwert")
    plt.plot(x, y_plus_std, marker="o", linestyle="--", label="Mittelwert + Standardabweichung")
    plt.plot(x, y_minus_std, marker="o", linestyle="--", label="Mittelwert - Standardabweichung")
    plt.plot(x, y_min, marker="o", linestyle=":", label="Minimum")
    plt.plot(x, y_max, marker="o", linestyle=":", label="Maximum")

    plt.xlabel("TSR (gemittelter Messwert)")
    plt.ylabel(coeff_label)
    plt.title(f"{coeff_label} über TSR bei Yaw = {yaw_value}°")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_name = f"{coeff_label}_mean_yaw_{int(yaw_value):+d}.png".replace("+", "plus").replace("-", "minus")
    plt.savefig(OUTPUT_DIR / out_name, dpi=200)
    plt.close()


def save_summary_csv(rows: list[dict]):
    import csv

    out_csv = OUTPUT_DIR / "cp_ct_mean_summary_by_test.csv"
    fieldnames = [
        "test", "yaw_target", "yaw_actual_mean", "pitot_velocity_mean", "free_air_velocity_mean", "ct_uncorrected_mean", "tsr_expected", "tsr_mean", "tsr_std",
        "cp_mean", "cp_plus_std", "cp_minus_std", "cp_min", "cp_max",
        "ct_mean", "ct_plus_std", "ct_minus_std", "ct_min", "ct_max",
        "mat_file",
    ]

    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not TEST_MATRIX_PATH.exists():
        raise FileNotFoundError(f"Excel-Datei nicht gefunden: {TEST_MATRIX_PATH}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"data-Ordner nicht gefunden: {DATA_DIR}")

    rows = build_dataframe_like_records()
    if not rows:
        raise RuntimeError("Es konnten keine Testdaten verarbeitet werden.")

    save_summary_csv(rows)

    yaw_values = sorted(set(r["yaw_target"] for r in rows if r["yaw_target"] is not None))
    for yaw in yaw_values:
        plot_for_yaw(rows, yaw, "cp")
        plot_for_yaw(rows, yaw, "ct")

    print("Fertig.")
    print(f"Ausgabeordner: {OUTPUT_DIR.resolve()}")
    print("Erzeugte Dateien:")
    for path in sorted(OUTPUT_DIR.iterdir()):
        print(" -", path.name)

    print("\nWICHTIG:")
    print("cP wurde aus Hub.Torque berechnet.")
    print("cT wurde aus Tower.FA über einen Hebelarm berechnet.")
    print(f"Verwendeter Kraftarm: {THRUST_LEVER_ARM_M} m")
    print(f"Gemeinsamer Messzeitraum: {MEASUREMENT_DURATION_S} s")
    print(f"Windkanal-Querschnitt: {TUNNEL_WIDTH_M} m x {TUNNEL_HEIGHT_M} m")
    print(f"Windkanal-Tiefe: {TUNNEL_DEPTH_M} m (nicht für alpha verwendet)")
    print(f"Blockage-Verhältnis alpha: {BLOCKAGE_RATIO:.4f}")
    print("TSR, cP und cT wurden mit der äquivalenten Freistrahlgeschwindigkeit berechnet.")
    print("Für die Kurven wird der arithmetische Mittelwert statt des Medians verwendet.")
    print("Falls euer Prüfstand einen anderen Kalibrierwert hat, bitte THRUST_LEVER_ARM_M anpassen.")


if __name__ == "__main__":
    main()
