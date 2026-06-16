"""
Column definitions and the row container shared by both test matrices.

A test-matrix row is split into three logical groups of columns:

1. Set-points the operator dials in (wind speed, pitch, rpm, yaw, and for Task 2
   the probe X/Y/Z position).
2. Derived / expected quantities (Reynolds, TSR, expected C_P and C_T, and the
   expected power / torque / thrust used to check the constraints).
3. Empty "to be filled in" columns for the data the G1 model records during the
   test (the instrumented channels listed in the task introduction).

Keeping the column names in one place guarantees the two Excel sheets stay
consistent and makes relabelling trivial.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Empty measurement columns: one per channel the G1 model provides. These are
# created blank so the team can paste the averaged measured values next to the
# planned set-points. (From "Data Provided by the G1 Model".)
G1_MEASUREMENT_COLUMNS: tuple[str, ...] = (
    "Meas. Rotor azimuth [deg]",
    "Meas. Rotor speed [rpm]",
    "Meas. Generator torque [Nm]",
    "Meas. Aerodynamic torque [Nm]",
    "Meas. Tower fore-aft moment [Nm]",
    "Meas. Tower side-side moment [Nm]",
    "Meas. Shaft bending moment [Nm]",
    "Meas. Demanded pitch B1 [deg]",
    "Meas. Actual pitch B1 [deg]",
    "Meas. Demanded pitch B2 [deg]",
    "Meas. Actual pitch B2 [deg]",
    "Meas. Demanded pitch B3 [deg]",
    "Meas. Actual pitch B3 [deg]",
    "Meas. Demanded yaw [deg]",
    "Meas. Actual yaw [deg]",
)


@dataclass(frozen=True)
class TestMatrixRow:
    """
    One row of a test matrix.

    The wake-probe position fields (probe_x/y/z) are only meaningful for Task 2;
    for Task 1 they are left as None and simply not written into the sheet.
    """

    test_number: int
    requested_tunnel_speed: float  # [m/s]  speed to set on the tunnel (blockage-corrected)
    equivalent_free_air_speed: float  # [m/s] U'_inf the rotor effectively feels
    blade_pitch_deg: float  # [deg]
    rotor_speed_rpm: float  # [rpm]
    yaw_deg: float  # [deg]
    reynolds: float  # [-]
    tsr: float  # [-]
    expected_cp: float  # [-]
    expected_ct_thrust: float  # [-]  THRUST coefficient
    expected_power_w: float  # [W]
    expected_torque_nm: float  # [Nm]
    expected_thrust_n: float  # [N]
    probe_x: float | None = None  # [mm]
    probe_y: float | None = None  # [mm]
    probe_z: float | None = None  # [mm]
    # Blank measurement slots, keyed by channel name (filled with empty strings).
    measurements: dict[str, str] = field(default_factory=dict)
