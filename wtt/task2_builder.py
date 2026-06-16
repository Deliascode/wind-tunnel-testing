"""
Task-2 (wake) test-matrix builder for Group 2.

Group 2 measures the wake at one downstream station (X = 2D) for yaw = 0, +30 and
-30 degrees, at the prescribed requested tunnel speed (5.4 m/s), the optimum blade
pitch and the optimum TSR.

The survey spans the full y-z plane at that station, so the wake cross-section can
be graphed and its center best-fitted (not just a single hub-height line):

* 9 points on the Y axis (Z = 0), cosine-clustered around the deflected wake
  center -- kept on the axis for the horizontal wake profile.
* Two concentric circles in the y-z plane, centred on the same wake center, with
  their points angularly offset so none lands on the Y axis (Z = 0). The circles
  sample the wake above and below hub height.

Per yaw: 9 + 6 + 8 = 23 points (69 total). The lateral wake-center shift is the
Jimenez deflection (unchanged).

Coordinate frame (Lecture 5 traverse system): the reported X/Y/Z are *traverse*
coordinates. Home X/Y/Z = 0 sits at hub height, 0.5 D_nom behind the rotor, so the
reported X = (distance behind the rotor) - home offset; Y and Z share their origin
with the hub center. Positions are reported in millimetres.
"""

from __future__ import annotations

import math

from .campaign_config import CampaignConfig
from .operating_point import OperatingPointResult, OperatingPointSolver
from .test_matrix_row import G1_MEASUREMENT_COLUMNS, TestMatrixRow
from .wake_model import (
    centered_lateral_positions,
    concentric_ring_positions,
    fitted_half_width,
    reachable_radius,
    wake_center_offset,
    wake_radius,
)


# Convert metres to millimetres for the reported probe positions.
_M_TO_MM: float = 1000.0


class Task2WakeBuilder:
    """Builds the wake-survey test matrix as a y-z plane per yaw."""

    def __init__(self, config: CampaignConfig, solver: OperatingPointSolver) -> None:
        self._config = config
        self._solver = solver

    def _optimum_tsr(self) -> float:
        """Optimum TSR taken from the look-up table's peak-C_P point."""
        return self._solver._table.optimum_operating_point().tsr  # noqa: SLF001

    # ----------------------------------------------------------------------
    # Geometry of one yaw plane
    # ----------------------------------------------------------------------
    def _wake_center_y(self, yaw_deg: float, thrust_coefficient: float) -> float:
        """Lateral (Y) wake-center offset from the Jimenez deflection model [m]."""
        return wake_center_offset(
            thrust_coefficient=thrust_coefficient,
            yaw_angle_rad=math.radians(yaw_deg),
            wake_expansion_coefficient=self._config.wake.wake_expansion_coefficient,
            rotor_diameter=self._config.rotor_diameter,
            downstream_distance=self._config.wake.downstream_distance,
        )

    def _hubline_positions(self, center_y: float) -> list[tuple[float, float]]:
        """9 (Y, Z = 0) points on the hub-height axis, centred on the wake center."""
        wake = self._config.wake
        desired_half_width = wake.span_factor * wake_radius(
            wake_expansion_coefficient=wake.wake_expansion_coefficient,
            rotor_diameter=self._config.rotor_diameter,
            downstream_distance=wake.downstream_distance,
        )
        half_width = fitted_half_width(
            wake_center_y=center_y,
            desired_half_width=desired_half_width,
            lower_limit=wake.y_min,
            upper_limit=wake.y_max,
        )
        y_positions = centered_lateral_positions(
            wake_center_y=center_y,
            half_width=half_width,
            number_of_points=wake.hubline_points,
        )
        return [(float(y), 0.0) for y in y_positions]

    def _ring_positions(self, center_y: float) -> list[tuple[float, float]]:
        """Concentric-circle (Y, Z) points around the wake center (off the axis)."""
        wake = self._config.wake
        max_radius = reachable_radius(
            wake_center_y=center_y,
            y_min=wake.y_min,
            y_max=wake.y_max,
            z_min=wake.z_min,
            z_max=wake.z_max,
        )
        positions: list[tuple[float, float]] = []
        for count, fraction in zip(wake.ring_point_counts, wake.ring_radius_fractions):
            y_ring, z_ring = concentric_ring_positions(
                wake_center_y=center_y,
                radius=fraction * max_radius,
                number_of_points=count,
            )
            positions.extend((float(y), float(z)) for y, z in zip(y_ring, z_ring))
        return positions

    def _plane_positions(self, center_y: float) -> list[tuple[float, float]]:
        """All (Y, Z) survey points for one yaw: hub-line axis points + circles."""
        return self._hubline_positions(center_y) + self._ring_positions(center_y)

    # ----------------------------------------------------------------------
    # Per-yaw operating point + plane
    # ----------------------------------------------------------------------
    def build_results(
        self,
    ) -> list[tuple[OperatingPointResult, list[tuple[float, float]]]]:
        """
        For each yaw, solve the (constant) operating point and its (Y, Z) plane.

        Returns a list of (operating_point_result, [(Y, Z), ...]) in metres, one
        entry per yaw case. The operating point uses the prescribed *requested
        tunnel speed* (5.4 m/s); the rotor feels the blockage-corrected free-air
        speed, and the resulting Reynolds number is reported.
        """
        pitch = self._config.targets.optimum_pitch_deg
        tunnel_speed = self._config.wake.requested_tunnel_speed
        tsr = self._optimum_tsr()

        results: list[tuple[OperatingPointResult, list[tuple[float, float]]]] = []
        for yaw in self._config.yaw.yaw_angles_deg:
            result = self._solver.solve_for_fixed_tunnel_speed(
                tsr=tsr,
                pitch_deg=pitch,
                yaw_deg=yaw,
                tunnel_speed=tunnel_speed,
            )
            center_y = self._wake_center_y(yaw, result.ct_thrust)
            positions = self._plane_positions(center_y)
            results.append((result, positions))
        return results

    def _traverse_x_mm(self) -> float:
        """Reported X = (distance behind rotor) - home offset, in millimetres."""
        x_m = self._config.wake.downstream_distance - self._config.traverse_home_offset
        return x_m * _M_TO_MM

    def build_rows(self) -> list[TestMatrixRow]:
        """Convert the per-yaw results and (Y, Z) planes into numbered rows."""
        rows: list[TestMatrixRow] = []
        empty_measurements = {name: "" for name in G1_MEASUREMENT_COLUMNS}
        x_mm = self._traverse_x_mm()

        test_number = 1
        for result, positions in self.build_results():
            for y_m, z_m in positions:
                rows.append(
                    TestMatrixRow(
                        test_number=test_number,
                        requested_tunnel_speed=result.requested_tunnel_speed,
                        equivalent_free_air_speed=result.equivalent_free_air_speed,
                        blade_pitch_deg=result.pitch_deg,
                        rotor_speed_rpm=result.rotor_speed_rpm,
                        yaw_deg=result.yaw_deg,
                        reynolds=result.reynolds,
                        tsr=result.tsr,
                        expected_cp=result.cp,
                        expected_ct_thrust=result.ct_thrust,
                        expected_power_w=result.power_w,
                        expected_torque_nm=result.torque_nm,
                        expected_thrust_n=result.thrust_n,
                        probe_x=x_mm,
                        probe_y=y_m * _M_TO_MM,
                        probe_z=z_m * _M_TO_MM,
                        measurements=dict(empty_measurements),
                    )
                )
                test_number += 1
        return rows

    # ----------------------------------------------------------------------
    # Traverse-file blocks (one per yaw): (X, Y, Z, A) tuples in millimetres
    # ----------------------------------------------------------------------
    def traverse_blocks(
        self,
    ) -> list[tuple[float, list[tuple[float, float, float, float]]]]:
        """
        (yaw, [(X, Y, Z, A), ...]) per yaw, for the tab-separated traverse files.

        The A (probe angle) column is always 0 -- the probe is never angled. The
        turbine yaw is a separate operating condition (set on the turntable and
        recorded in the Excel matrix), not encoded in the traverse file. Positions
        are traverse coordinates in millimetres.
        """
        x_mm = self._traverse_x_mm()
        blocks: list[tuple[float, list[tuple[float, float, float, float]]]] = []
        for result, positions in self.build_results():
            lines = [
                (x_mm, y_m * _M_TO_MM, z_m * _M_TO_MM, 0.0) for y_m, z_m in positions
            ]
            blocks.append((result.yaw_deg, lines))
        return blocks
