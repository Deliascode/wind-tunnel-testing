from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.io import loadmat
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


# ============================================================
# Paths and constants
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "measured_variable_statistics"

RESULTS_FILE_NUMBER = 5
TOP_START = 1
TOP_END = 31

MEASUREMENT_DURATION_S = 8.0
TARGET_LENGTH = 2000

# G1 geometry / unit assumptions used by the newest processing scripts.
ROTOR_RADIUS_M = 0.5436
ROTOR_AREA_M2 = math.pi * ROTOR_RADIUS_M**2

# Hub torque / hub bending channels are stored as mNm in the available examples.
HUB_TORQUE_SCALE_TO_NM = 1e-3
HUB_BENDING_MOMENT_SCALE_TO_NM = 1e-3

# Used only when generator torque is computed from PowerReference.Abs.
RPM_TO_RAD_PER_S = 2.0 * math.pi / 60.0

# CSV names.
SUMMARY_CSV_NAME = "measured_variables_statistics_by_top_with_omega_min_max_de.csv"
SUMMARY_XLSX_NAME = "measured_variables_statistics_by_top_with_omega_min_max.xlsx"
FORMULAS_CSV_NAME = "measured_variables_formulas.csv"


# ============================================================
# MATLAB struct helpers
# ============================================================

def unwrap_singleton(value):
    current = value

    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.flat[0]

    return current


def get_array(value) -> np.ndarray:
    array = np.asarray(unwrap_singleton(value), dtype=float).ravel(order="C")

    if array.size == 0:
        return np.array([np.nan], dtype=float)

    return array


def safe_get_nested(obj, path: str) -> np.ndarray:
    """Reads a nested field path like 'Pitch.Blade1Dem'.

    Missing fields return a one-value NaN array so the CSV structure remains
    stable even if a file is incomplete.
    """

    current = obj

    try:
        for part in path.split("."):
            current = getattr(current, part)
        return get_array(current)
    except AttributeError:
        return np.array([np.nan], dtype=float)


def load_model1(mat_path: Path):
    mat_data = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False,
    )
    return mat_data["Data"].ModelsData.Model1


# ============================================================
# Resampling rules
# ============================================================

def block_average_to_target_length(values: np.ndarray, target_length: int) -> np.ndarray:
    """Downsamples by block averaging.

    Example:
    20000 samples -> 2000 samples means 2000 blocks with 10 samples each.
    This is used for 2.5 kHz channels such as Hub.Torque, Azimuth and
    Hub.Yawing/Nodding when they are combined with 250 Hz signals.
    """

    values = np.asarray(values, dtype=float).ravel(order="C")

    if values.size % target_length != 0:
        raise ValueError(
            "Block averaging requires the signal length to be an integer "
            "multiple of target_length."
        )

    block_size = values.size // target_length
    blocks = values.reshape(target_length, block_size)

    with np.errstate(invalid="ignore"):
        return np.nanmean(blocks, axis=1)


def interpolate_to_target_length(
    values: np.ndarray,
    target_length: int,
    duration_s: float = MEASUREMENT_DURATION_S,
) -> np.ndarray:
    """Linearly interpolates a signal over the common measurement duration."""

    values = np.asarray(values, dtype=float).ravel(order="C")

    if target_length <= 0:
        raise ValueError("target_length must be greater than zero.")

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
        return np.full(target_length, values[finite_mask][0], dtype=float)

    source_time = np.linspace(
        0.0,
        duration_s,
        values.size,
        endpoint=False,
    )
    target_time = np.linspace(
        0.0,
        duration_s,
        target_length,
        endpoint=False,
    )

    return np.interp(
        target_time,
        source_time[finite_mask],
        values[finite_mask],
    )


def resample_to_2000(values: np.ndarray, signal_name: str) -> np.ndarray:
    """Resamples every signal to 2000 values.

    Rules:
    - 2000-sample signals remain unchanged.
    - Longer integer-ratio signals are block-averaged.
      This is intended for 20000 -> 2000 channels.
    - Shorter signals are interpolated.
      This is intended for AirDensity / PowerReference 1000 -> 2000.
    """

    values = np.asarray(values, dtype=float).ravel(order="C")

    if values.size == TARGET_LENGTH:
        return values.astype(float, copy=False)

    if values.size > TARGET_LENGTH and values.size % TARGET_LENGTH == 0:
        return block_average_to_target_length(values, TARGET_LENGTH)

    return interpolate_to_target_length(values, TARGET_LENGTH)


# ============================================================
# Statistics
# ============================================================

def fill_nonfinite(values: np.ndarray) -> np.ndarray:
    """Fills invalid values linearly before the Fourier transform."""

    values = np.asarray(values, dtype=float).copy()
    finite = np.isfinite(values)

    if finite.sum() == 0:
        return np.full_like(values, np.nan)

    if finite.sum() == 1:
        return np.full_like(values, values[finite][0])

    if not finite.all():
        indices = np.arange(values.size)
        values[~finite] = np.interp(
            indices[~finite],
            indices[finite],
            values[finite],
        )

    return values


def finite_stat(values: np.ndarray, function: Callable[[np.ndarray], float]) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if values.size == 0:
        return math.nan

    return float(function(values))


def fourier_dc(values: np.ndarray) -> float:
    """Returns the normalized zero-frequency FFT component.

    This is the scalar Fourier value used in the previous FFT scripts. It is
    the DC component and equals the arithmetic mean of the filled time series.
    It is not the dominant frequency.
    """

    values = fill_nonfinite(values)

    if values.size == 0 or not np.isfinite(values).any():
        return math.nan

    fft_values = np.fft.rfft(values)
    return float(np.real(fft_values[0]) / values.size)


def three_statistics(values: np.ndarray) -> dict[str, float]:
    return {
        "fourier": fourier_dc(values),
        "mean": finite_stat(values, np.mean),
        "median": finite_stat(values, np.median),
    }


# ============================================================
# Variable calculations
# ============================================================

def omega_from_rpm(rotor_speed_rpm: np.ndarray) -> np.ndarray:
    return rotor_speed_rpm * RPM_TO_RAD_PER_S


def safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)

    return np.divide(
        numerator,
        denominator,
        out=np.full(TARGET_LENGTH, np.nan, dtype=float),
        where=(
            np.isfinite(numerator)
            & np.isfinite(denominator)
            & (denominator != 0.0)
        ),
    )


def calculate_time_series(model1) -> dict[str, np.ndarray]:
    """Builds all requested 2000-sample time series for one MAT file."""

    rotor_speed_rpm = resample_to_2000(
        safe_get_nested(model1, "RotorSpeed"),
        "RotorSpeed",
    )
    omega = omega_from_rpm(rotor_speed_rpm)

    azimuth = resample_to_2000(
        safe_get_nested(model1, "Azimuth"),
        "Azimuth",
    )

    # Generator torque is reconstructed from PowerReference.Abs and rotor speed:
    # Q_generator = P_reference_abs / omega.
    # Assumption: PowerReference.Abs is in W.
    power_reference_abs = resample_to_2000(
        safe_get_nested(model1, "PowerReference.Abs"),
        "PowerReference.Abs",
    )
    generator_torque_nm = safe_divide(power_reference_abs, omega)

    # Aerodynamic torque is the measured hub torque, scaled from mNm to Nm.
    aerodynamic_torque_nm = (
        resample_to_2000(
            safe_get_nested(model1, "Hub.Torque"),
            "Hub.Torque",
        )
        * HUB_TORQUE_SCALE_TO_NM
    )

    tower_fa_moment_nm = resample_to_2000(
        safe_get_nested(model1, "Tower.FA"),
        "Tower.FA",
    )
    tower_ss_moment_nm = resample_to_2000(
        safe_get_nested(model1, "Tower.SS"),
        "Tower.SS",
    )

    hub_yawing_nm = (
        resample_to_2000(
            safe_get_nested(model1, "Hub.Yawing"),
            "Hub.Yawing",
        )
        * HUB_BENDING_MOMENT_SCALE_TO_NM
    )
    hub_nodding_nm = (
        resample_to_2000(
            safe_get_nested(model1, "Hub.Nodding"),
            "Hub.Nodding",
        )
        * HUB_BENDING_MOMENT_SCALE_TO_NM
    )
    shaft_bending_moment_nm = np.sqrt(hub_yawing_nm**2 + hub_nodding_nm**2)

    # Pitch mapping follows the user's specified folder mapping exactly.
    demanded_pitch_b1_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade1"),
        "Pitch.Blade1",
    )
    actual_pitch_b1_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade1Dem"),
        "Pitch.Blade1Dem",
    )

    demanded_pitch_b2_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade2"),
        "Pitch.Blade2",
    )
    actual_pitch_b2_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade2Dem"),
        "Pitch.Blade2Dem",
    )

    demanded_pitch_b3_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade3"),
        "Pitch.Blade3",
    )
    actual_pitch_b3_deg = resample_to_2000(
        safe_get_nested(model1, "Pitch.Blade3Dem"),
        "Pitch.Blade3Dem",
    )

    demanded_yaw_deg = resample_to_2000(
        safe_get_nested(model1, "YawDem"),
        "YawDem",
    )
    actual_yaw_deg = resample_to_2000(
        safe_get_nested(model1, "Yaw"),
        "Yaw",
    )

    return {
        "Meas. Rotor azimuth [deg]": azimuth,
        "Meas. Rotor speed [rpm]": rotor_speed_rpm,
        "Omega [rad/s]": omega,
        "Meas. Generator torque [Nm]": generator_torque_nm,
        "Meas. Aerodynamic torque [Nm]": aerodynamic_torque_nm,
        "Meas. Tower fore-aft moment [Nm]": tower_fa_moment_nm,
        "Meas. Tower side-side moment [Nm]": tower_ss_moment_nm,
        "Meas. Shaft bending moment [Nm]": shaft_bending_moment_nm,
        "Meas. Demanded pitch B1 [deg]": demanded_pitch_b1_deg,
        "Meas. Actual pitch B1 [deg]": actual_pitch_b1_deg,
        "Meas. Demanded pitch B2 [deg]": demanded_pitch_b2_deg,
        "Meas. Actual pitch B2 [deg]": actual_pitch_b2_deg,
        "Meas. Demanded pitch B3 [deg]": demanded_pitch_b3_deg,
        "Meas. Actual pitch B3 [deg]": actual_pitch_b3_deg,
        "Meas. Demanded yaw [deg]": demanded_yaw_deg,
        "Meas. Actual yaw [deg]": actual_yaw_deg,
    }


FORMULA_ROWS = [
    {
        "variable": "Meas. Rotor azimuth [deg]",
        "source": "Data.ModelsData.Model1.Azimuth",
        "formula": "Measured channel; 20000 -> 2000 by block averaging.",
    },
    {
        "variable": "Meas. Rotor speed [rpm]",
        "source": "Data.ModelsData.Model1.RotorSpeed",
        "formula": "Measured channel; kept at 2000 samples.",
    },
    {
        "variable": "Omega [rad/s]",
        "source": "Data.ModelsData.Model1.RotorSpeed",
        "formula": "omega = RotorSpeed * 2*pi/60. RotorSpeed is measured in rpm; omega is in rad/s. Uses the 2000-sample resampled RotorSpeed time series. Additional columns report min(omega), max(omega), and median(omega).",
    },
    {
        "variable": "Meas. Generator torque [Nm]",
        "source": "Data.ModelsData.Model1.PowerReference.Abs and RotorSpeed",
        "formula": "Q_generator = PowerReference.Abs / omega, omega = RotorSpeed * 2*pi/60. Assumption: PowerReference.Abs is power in W.",
    },
    {
        "variable": "Meas. Aerodynamic torque [Nm]",
        "source": "Data.ModelsData.Model1.Hub.Torque",
        "formula": "Q_aero = Hub.Torque * 1e-3. Assumption: raw Hub.Torque is in mNm.",
    },
    {
        "variable": "Meas. Tower fore-aft moment [Nm]",
        "source": "Data.ModelsData.Model1.Tower.FA",
        "formula": "Measured tower-base fore-aft bending moment; kept at 2000 samples.",
    },
    {
        "variable": "Meas. Tower side-side moment [Nm]",
        "source": "Data.ModelsData.Model1.Tower.SS",
        "formula": "Measured tower-base side-side bending moment; kept at 2000 samples.",
    },
    {
        "variable": "Meas. Shaft bending moment [Nm]",
        "source": "Data.ModelsData.Model1.Hub.Yawing and Hub.Nodding",
        "formula": "M_shaft = sqrt((Hub.Yawing*1e-3)^2 + (Hub.Nodding*1e-3)^2). Assumption: raw yawing/nodding moments are in mNm.",
    },
    {
        "variable": "Meas. Demanded pitch B1 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade1",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Actual pitch B1 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade1Dem",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Demanded pitch B2 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade2",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Actual pitch B2 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade2Dem",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Demanded pitch B3 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade3",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Actual pitch B3 [deg]",
        "source": "Data.ModelsData.Model1.Pitch.Blade3Dem",
        "formula": "Measured channel; mapping follows user instruction.",
    },
    {
        "variable": "Meas. Demanded yaw [deg]",
        "source": "Data.ModelsData.Model1.YawDem",
        "formula": "Measured demanded yaw channel; kept at 2000 samples.",
    },
    {
        "variable": "Meas. Actual yaw [deg]",
        "source": "Data.ModelsData.Model1.Yaw",
        "formula": "Measured actual yaw channel; kept at 2000 samples.",
    },
]


# ============================================================
# CSV writers
# ============================================================

def make_output_headers() -> list[str]:
    headers = [
        "top",
        "mat_file",
        "file_found",
    ]

    for formula_row in FORMULA_ROWS:
        variable = formula_row["variable"]

        # Keep one spare/blank column before the omega block.
        if variable == "Omega [rad/s]":
            headers.append("")

        headers.extend(
            [
                f"{variable} Fourier DC",
                f"{variable} Mean",
                f"{variable} Median",
            ]
        )

        if variable == "Omega [rad/s]":
            headers.extend(
                [
                    "Omega [rad/s] Minimum",
                    "Omega [rad/s] Maximum",
                    "Omega [rad/s] Median check",
                ]
            )

    return headers


def empty_statistics_row(top: int, mat_name: str) -> dict:
    row = {
        "top": top,
        "mat_file": mat_name,
        "file_found": False,
    }

    for header in make_output_headers()[3:]:
        row[header] = "" if header == "" else math.nan

    return row


def process_mat_file(top: int, mat_path: Path) -> dict:
    model1 = load_model1(mat_path)
    time_series = calculate_time_series(model1)

    row = {
        "top": top,
        "mat_file": mat_path.name,
        "file_found": True,
        "": "",
    }

    for variable_name, values in time_series.items():
        stats = three_statistics(values)
        row[f"{variable_name} Fourier DC"] = stats["fourier"]
        row[f"{variable_name} Mean"] = stats["mean"]
        row[f"{variable_name} Median"] = stats["median"]

    return row



def format_csv_value(value):
    """Formats values for German Excel CSV import.

    The CSV uses semicolon as delimiter and comma as decimal separator.
    This avoids German Excel interpreting decimal dots as thousands separators.
    """

    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            return "nan"
        return f"{float(value):.10g}".replace(".", ",")

    if isinstance(value, (int, np.integer)):
        return int(value)

    return value


def write_summary_xlsx(rows: list[dict]) -> Path:
    """Writes an Excel workbook with real numeric cells and readable widths."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / SUMMARY_XLSX_NAME
    headers = make_output_headers()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Statistics"

    worksheet.append(headers)

    for row in rows:
        worksheet.append([row.get(header, math.nan) for header in headers])

    # Freeze headers.
    worksheet.freeze_panes = "A2"

    # Make columns readable without changing the stored numeric values.
    for column_index, header in enumerate(headers, start=1):
        column_letter = get_column_letter(column_index)
        if header == "":
            worksheet.column_dimensions[column_letter].width = 4
        elif column_index <= 3:
            worksheet.column_dimensions[column_letter].width = max(12, len(header) + 2)
        else:
            worksheet.column_dimensions[column_letter].width = 18

    workbook.save(output_path)
    return output_path


def write_summary_csv(rows: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / SUMMARY_CSV_NAME
    headers = make_output_headers()

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=headers,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    header: format_csv_value(row.get(header, math.nan))
                    for header in headers
                }
            )

    return output_path


def write_formulas_csv() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / FORMULAS_CSV_NAME

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["variable", "source", "formula"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(FORMULA_ROWS)

    return output_path


# ============================================================
# Main
# ============================================================

def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

    rows = []

    for top in range(TOP_START, TOP_END + 1):
        mat_name = f"Results_File_{RESULTS_FILE_NUMBER}_TOP_{top}.mat"
        mat_path = DATA_DIR / mat_name

        if not mat_path.exists():
            print(f"Missing file, writing empty row: {mat_name}")
            rows.append(empty_statistics_row(top, mat_name))
            continue

        rows.append(process_mat_file(top, mat_path))

    summary_csv = write_summary_csv(rows)
    summary_xlsx = write_summary_xlsx(rows)
    formulas_csv = write_formulas_csv()

    print("Finished.")
    print(f"German Excel CSV: {summary_csv.resolve()}")
    print(f"Excel workbook: {summary_xlsx.resolve()}")
    print(f"Formula/source CSV: {formulas_csv.resolve()}")
    print(f"Processed TOP {TOP_START} to TOP {TOP_END} for Results_File_{RESULTS_FILE_NUMBER}.")
    print("Fourier DC is the normalized 0 Hz FFT component, not the dominant frequency.")
    print("Added one spare column before omega and six omega columns: Fourier DC, mean, median, minimum, maximum, median check.")
    print("Omega formula: omega = RotorSpeed * 2*pi/60, using RotorSpeed in rpm.")
    print("Omega min/max/median columns use the same omega time series.")
    print("Azimuth is a circular angle; ordinary mean/median/Fourier DC can be misleading near the 0/360 wrap.")


if __name__ == "__main__":
    main()
