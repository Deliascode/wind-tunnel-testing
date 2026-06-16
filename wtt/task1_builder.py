"""
Task-1 (performance) test-matrix builder for Group 2.

Group 2 measures three performance curves at yaw = 0, +30 and -30 degrees, each
at Re = 75000 (+/- 2000) and the optimum blade pitch.

Design (new): the *requested tunnel speed* is the hardest quantity to dial in, so
it is set on a coarse grid of 0.5 m/s steps rather than computed to arbitrary
precision. For every grid speed the rotor speed (the TSR) is the free knob used
to hit Re = 75000 exactly, and each speed is tested at all three yaw angles.

The grid only spans the speed band where Re = 75000 is reachable for every yaw
inside the TSR limits [5.5, 9]. After solving, each candidate is checked against
the power / torque / rotor-speed limits; a speed is kept only if all three of its
yaw points pass, so the three curves always share the same set of wind speeds.
This can yield fewer than 30 points, which is fine (30 is the maximum). The rows
are finally ordered by ascending requested wind speed (then yaw).
"""

from __future__ import annotations

import math

from .campaign_config import CampaignConfig
from .constraints import check_row
from .operating_point import OperatingPointResult, OperatingPointSolver
from .test_matrix_row import G1_MEASUREMENT_COLUMNS, TestMatrixRow


# Hard cap on the number of performance points (assignment maximum).
_MAX_POINTS: int = 30


class Task1PerformanceBuilder:
    """Builds the performance test matrix (constant Re, speed grid, 3 yaws)."""

    def __init__(self, config: CampaignConfig, solver: OperatingPointSolver) -> None:
        self._config = config
        self._solver = solver

    # ----------------------------------------------------------------------
    # Feasible requested-speed band (Re = 75000 reachable for every yaw)
    # ----------------------------------------------------------------------
    def _feasible_speed_band(self) -> tuple[float, float]:
        """
        Requested-speed range over which Re = 75000 is reachable for all yaws.

        At constant Re the required tunnel speed is highest at the lowest TSR and
        lowest at the highest TSR. Solving the Re calibration at the two TSR limits
        therefore brackets the achievable speed range for each yaw; the band common
        to every yaw is the intersection of those ranges.
        """
        pitch = self._config.targets.optimum_pitch_deg
        target_re = self._config.targets.target_reynolds
        tsr_min = self._config.constraints.tsr_min
        tsr_max = self._config.constraints.tsr_max
        yaws = self._config.yaw.yaw_angles_deg

        # Highest TSR -> lowest required speed (the low end of each yaw's range).
        low_ends = [
            self._solver.solve_for_target_reynolds(
                tsr=tsr_max, pitch_deg=pitch, yaw_deg=yaw, target_reynolds=target_re
            ).requested_tunnel_speed
            for yaw in yaws
        ]
        # Lowest TSR -> highest required speed (the high end of each yaw's range).
        high_ends = [
            self._solver.solve_for_target_reynolds(
                tsr=tsr_min, pitch_deg=pitch, yaw_deg=yaw, target_reynolds=target_re
            ).requested_tunnel_speed
            for yaw in yaws
        ]
        return max(low_ends), min(high_ends)

    def _speed_grid(self) -> list[float]:
        """
        Requested speeds on a 0.5 m/s grid, from the lowest feasible speed up.

        The first grid point is the smallest multiple of the step at or above the
        feasible band's lower edge; the last is the largest multiple at or below
        the upper edge.
        """
        band_low, band_high = self._feasible_speed_band()
        step = self._config.performance_speed_step
        first = math.ceil(band_low / step) * step

        speeds: list[float] = []
        speed = first
        while speed <= band_high + 1e-9:
            speeds.append(round(speed, 3))
            speed += step
        return speeds

    def _within_limits(self, result: OperatingPointResult) -> bool:
        """True if a solved point satisfies every Group-2 limit (Re enforced)."""
        return not check_row(
            result=result,
            constraints=self._config.constraints,
            target_reynolds=self._config.targets.target_reynolds,
            enforce_reynolds=True,
        )

    def build_results(self) -> list[OperatingPointResult]:
        """
        Solve every kept (speed, yaw) operating point, ordered by ascending speed.

        For each grid speed all three yaw points are solved (TSR chosen so that
        Re = 75000). The speed is kept only if all three points satisfy the limits,
        guaranteeing the three yaw curves share the same wind speeds. The result is
        sorted by requested speed, then yaw, and capped at the 30-point maximum.
        """
        pitch = self._config.targets.optimum_pitch_deg
        target_re = self._config.targets.target_reynolds
        tsr_min = self._config.constraints.tsr_min
        tsr_max = self._config.constraints.tsr_max

        kept: list[OperatingPointResult] = []
        for speed in self._speed_grid():
            trio = [
                self._solver.solve_for_target_reynolds_at_tunnel_speed(
                    tunnel_speed=speed,
                    pitch_deg=pitch,
                    yaw_deg=yaw,
                    target_reynolds=target_re,
                    tsr_min=tsr_min,
                    tsr_max=tsr_max,
                )
                for yaw in self._config.yaw.yaw_angles_deg
            ]
            if all(self._within_limits(result) for result in trio):
                kept.extend(trio)

        kept.sort(key=lambda r: (round(r.requested_tunnel_speed, 3), r.yaw_deg))
        return kept[:_MAX_POINTS]

    def build_rows(self) -> list[TestMatrixRow]:
        """Convert the physics results into numbered test-matrix rows."""
        rows: list[TestMatrixRow] = []
        empty_measurements = {name: "" for name in G1_MEASUREMENT_COLUMNS}

        for index, result in enumerate(self.build_results(), start=1):
            rows.append(
                TestMatrixRow(
                    test_number=index,
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
                    measurements=dict(empty_measurements),
                )
            )
        return rows
