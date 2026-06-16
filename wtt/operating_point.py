"""
Operating-point solver: the single place where the physics chain is assembled.

Given a target operating point (TSR, blade pitch, yaw) this class runs every
step in order and returns all the derived quantities that a test-matrix row
needs. Both the Task-1 and Task-2 builders use it, so the physics lives in one
place only.

Chain of steps
--------------
1. Look up the aerodynamic coefficients at (TSR, pitch):
       C_P, C_T(thrust), a (axial induction), a' (tangential induction).
   The tangential induction a' is obtained from BEM consistency:
       torque coefficient C_Q relates to a' through the annulus torque balance.
   For the reference (midspan) section we use the simple, table-consistent value
   a' computed from the local momentum relation; to keep things robust and
   table-driven we derive a' from C_Q and the axial induction (see below).
1b. Apply the yaw correction (see `wtt.yaw_model`): the look-up table has no yaw
   dependence, so C_P and C_T are multiplied by cosine-law factors (cos^3 for
   power, cos^2 for thrust) plus a small sign-dependent rotational-asymmetry term
   so that +gamma and -gamma differ. The induction factors are left uncorrected
   because they feed the (essentially yaw-independent) Reynolds calibration.
2. Calibrate the equivalent free-air speed U'_inf so the midspan Reynolds number
   equals the target (only for the performance task; the wake task fixes U).
3. Apply the Glauert blockage correction to get the tunnel command speed U_inf.
4. Convert TSR -> omega -> rpm using U'_inf (the speed the rotor feels).
5. Compute dimensional power / thrust / torque from the coefficients and U'_inf.

No fallbacks: every input must be present; out-of-range look-ups raise.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from scipy.optimize import brentq

from .aerodynamics import omega_from_tsr, rpm_from_omega
from .air_properties import AirProperties
from .blockage import blockage_ratio, commanded_tunnel_speed, glauert_speed_ratio
from .lookup_table import G1LookUpTable
from .performance import (
    aerodynamic_power,
    aerodynamic_thrust,
    aerodynamic_torque,
    rotor_disk_area,
)
from .reynolds_calibration import ReynoldsCalibrator
from .yaw_model import YawPerformanceModel


@dataclass(frozen=True)
class OperatingPointResult:
    """All quantities derived for a single (TSR, pitch, yaw) operating point."""

    tsr: float
    pitch_deg: float
    yaw_deg: float
    equivalent_free_air_speed: float  # [m/s]  U'_inf felt by the rotor
    requested_tunnel_speed: float  # [m/s]     U_inf to command on the tunnel
    rotor_speed_rpm: float  # [rpm]
    reynolds: float  # [-]
    cp: float  # [-]
    ct_thrust: float  # [-]
    axial_induction: float  # [-]
    tangential_induction: float  # [-]
    power_w: float  # [W]
    thrust_n: float  # [N]
    torque_nm: float  # [Nm]


def tangential_induction_from_torque(
    torque_coefficient: float,
    tsr: float,
    axial_induction: float,
) -> float:
    """
    Estimate the tangential induction factor a' consistent with the table.

    Rotor-integrated torque coefficient relates to the angular induction via the
    annulus torque balance. Using the disk-averaged relation

        C_Q = 8/(lambda) * integral a'(1-a) ... (full BEM),

    which for a representative section reduces to the local momentum result

        a' = C_Q / (4 * lambda * (1 - a))   (approximate, table-consistent),

    we obtain a small positive swirl factor. This keeps a' tied to the look-up
    data rather than guessed. `lambda` = TSR.
    """
    return torque_coefficient / (4.0 * tsr * (1.0 - axial_induction))


class OperatingPointSolver:
    """Runs the full physics chain for one operating point."""

    def __init__(
        self,
        lookup_table: G1LookUpTable,
        air: AirProperties,
        tunnel_cross_section_area: float,
        reynolds_calibrator: ReynoldsCalibrator,
        yaw_model: YawPerformanceModel,
    ) -> None:
        self._table = lookup_table
        self._air = air
        self._tunnel_area = tunnel_cross_section_area
        self._calibrator = reynolds_calibrator
        self._yaw_model = yaw_model
        # Geometry constants used repeatedly.
        self._tip_radius = lookup_table.tip_radius()
        self._rotor_area = rotor_disk_area(self._tip_radius)
        self._blockage = blockage_ratio(self._rotor_area, tunnel_cross_section_area)

    # ----------------------------------------------------------------------
    # Coefficient bundle at an operating point
    # ----------------------------------------------------------------------
    def _coefficients(self, tsr: float, pitch_deg: float):
        """Look up C_P, C_T(thrust), C_Q(torque) and induction factors a, a'."""
        cp = self._table.power_coefficient(tsr, pitch_deg)
        ct_thrust = self._table.thrust_coefficient(tsr, pitch_deg)
        cq_torque = self._table.torque_coefficient(tsr, pitch_deg)
        axial = self._table.axial_induction(tsr, pitch_deg)
        tangential = tangential_induction_from_torque(cq_torque, tsr, axial)
        return cp, ct_thrust, axial, tangential

    def _apply_yaw(
        self, cp_base: float, ct_base: float, yaw_deg: float, tsr: float
    ) -> tuple[float, float]:
        """
        Apply the yaw-dependent correction to the base (yaw-free) coefficients.

        Returns the corrected (C_P, C_T) for the given yaw. The induction factors
        are deliberately NOT corrected here: they feed the Reynolds calibration,
        which is governed by the rotor speed we set (dominated by the rotational
        component of the relative velocity) and is essentially yaw-independent.
        """
        yaw_rad = math.radians(yaw_deg)
        cp = cp_base * self._yaw_model.power_factor(yaw_rad, tsr)
        ct = ct_base * self._yaw_model.thrust_factor(yaw_rad, tsr)
        return cp, ct

    # ----------------------------------------------------------------------
    # Performance task: speed is found by Reynolds calibration
    # ----------------------------------------------------------------------
    def solve_for_target_reynolds(
        self,
        tsr: float,
        pitch_deg: float,
        yaw_deg: float,
        target_reynolds: float,
    ) -> OperatingPointResult:
        """
        Operating point where U'_inf is chosen so midspan Re = target_reynolds.

        This is the Task-1 path: we build constant-Reynolds performance curves,
        so for every TSR we re-solve the wind speed that hits Re = 75000.
        """
        cp_base, ct_base, axial, tangential = self._coefficients(tsr, pitch_deg)
        cp, ct_thrust = self._apply_yaw(cp_base, ct_base, yaw_deg, tsr)

        free_air_speed = self._calibrator.solve_speed_for_target_reynolds(
            target_reynolds=target_reynolds,
            tsr=tsr,
            axial_induction=axial,
            tangential_induction=tangential,
        )

        return self._assemble_result(
            tsr=tsr,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            free_air_speed=free_air_speed,
            cp=cp,
            ct_thrust=ct_thrust,
            axial=axial,
            tangential=tangential,
        )

    # ----------------------------------------------------------------------
    # Wake task: the COMMANDED tunnel speed is prescribed (5.4 m/s)
    # ----------------------------------------------------------------------
    def _free_air_speed_from_tunnel(
        self, tunnel_speed: float, thrust_coefficient: float
    ) -> float:
        """
        Equivalent free-air speed the rotor feels for a commanded tunnel speed.

        Inverse of the blockage command: U'_inf = U_tunnel * Glauert factor. The
        thrust coefficient must be the (yaw-corrected) rotor thrust coefficient,
        because blockage scales with the actual rotor loading.
        """
        return tunnel_speed * glauert_speed_ratio(thrust_coefficient, self._blockage)

    def solve_for_fixed_tunnel_speed(
        self,
        tsr: float,
        pitch_deg: float,
        yaw_deg: float,
        tunnel_speed: float,
    ) -> OperatingPointResult:
        """
        Operating point where the COMMANDED tunnel speed is prescribed.

        This is the Task-2 path: the wake task fixes the *requested tunnel speed*
        (5.4 m/s). The walls accelerate the flow, so the rotor actually feels the
        higher free-air speed U'_inf = tunnel_speed * Glauert factor. The resulting
        Reynolds number is reported (it need not equal 75000).
        """
        cp_base, ct_base, axial, tangential = self._coefficients(tsr, pitch_deg)
        cp, ct_thrust = self._apply_yaw(cp_base, ct_base, yaw_deg, tsr)
        free_air_speed = self._free_air_speed_from_tunnel(tunnel_speed, ct_thrust)
        return self._assemble_result(
            tsr=tsr,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            free_air_speed=free_air_speed,
            cp=cp,
            ct_thrust=ct_thrust,
            axial=axial,
            tangential=tangential,
        )

    # ----------------------------------------------------------------------
    # Performance task (new design): fixed tunnel speed, TSR solved for target Re
    # ----------------------------------------------------------------------
    def solve_for_target_reynolds_at_tunnel_speed(
        self,
        tunnel_speed: float,
        pitch_deg: float,
        yaw_deg: float,
        target_reynolds: float,
        tsr_min: float,
        tsr_max: float,
    ) -> OperatingPointResult:
        """
        Operating point at a fixed COMMANDED tunnel speed hitting a target Re.

        Under the new Task-1 design the tunnel speed is dialled in on a coarse
        0.5 m/s grid (it is the hardest quantity to set), and the rotor speed (the
        TSR) is the free knob used to reach Re = target. We root-solve the TSR in
        [tsr_min, tsr_max] whose midspan Reynolds number equals the target at this
        tunnel speed.

        No fallback: the caller restricts the speed grid to the band where the
        target is reachable, so the root is bracketed; otherwise brentq raises.
        """

        def residual(tsr: float) -> float:
            cp_base, ct_base, axial, tangential = self._coefficients(tsr, pitch_deg)
            _cp, ct_thrust = self._apply_yaw(cp_base, ct_base, yaw_deg, tsr)
            free_air_speed = self._free_air_speed_from_tunnel(tunnel_speed, ct_thrust)
            reynolds = self._calibrator.reynolds_at_speed(
                free_stream_speed=free_air_speed,
                tsr=tsr,
                axial_induction=axial,
                tangential_induction=tangential,
            )
            return reynolds - target_reynolds

        tsr = brentq(residual, tsr_min, tsr_max)
        # Re-assemble cleanly at the solved TSR (reuses the fixed-tunnel-speed path).
        return self.solve_for_fixed_tunnel_speed(
            tsr=tsr,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            tunnel_speed=tunnel_speed,
        )

    # ----------------------------------------------------------------------
    # Shared assembly of the dimensional results
    # ----------------------------------------------------------------------
    def _assemble_result(
        self,
        tsr: float,
        pitch_deg: float,
        yaw_deg: float,
        free_air_speed: float,
        cp: float,
        ct_thrust: float,
        axial: float,
        tangential: float,
    ) -> OperatingPointResult:
        """Finish the chain: Reynolds, blockage, rpm and dimensional loads."""
        # Reynolds actually achieved at this free-air speed.
        reynolds = self._calibrator.reynolds_at_speed(
            free_stream_speed=free_air_speed,
            tsr=tsr,
            axial_induction=axial,
            tangential_induction=tangential,
        )

        # Blockage correction: tunnel command speed is lower than the free-air speed.
        tunnel_speed = commanded_tunnel_speed(
            equivalent_free_air_speed=free_air_speed,
            thrust_coefficient=ct_thrust,
            blockage_ratio_value=self._blockage,
        )

        # Rotor speed from TSR and the free-air speed the rotor feels.
        omega = omega_from_tsr(tsr, free_air_speed, self._tip_radius)
        rpm = rpm_from_omega(omega)

        # Dimensional loads, evaluated with the free-air speed.
        power = aerodynamic_power(
            air_density=self._air.density,
            rotor_area=self._rotor_area,
            flow_speed=free_air_speed,
            power_coefficient=cp,
        )
        thrust = aerodynamic_thrust(
            air_density=self._air.density,
            rotor_area=self._rotor_area,
            flow_speed=free_air_speed,
            thrust_coefficient=ct_thrust,
        )
        torque = aerodynamic_torque(power=power, omega=omega)

        return OperatingPointResult(
            tsr=tsr,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            equivalent_free_air_speed=free_air_speed,
            requested_tunnel_speed=tunnel_speed,
            rotor_speed_rpm=rpm,
            reynolds=reynolds,
            cp=cp,
            ct_thrust=ct_thrust,
            axial_induction=axial,
            tangential_induction=tangential,
            power_w=power,
            thrust_n=thrust,
            torque_nm=torque,
        )

    # Exposed for reporting / sanity checks.
    def blockage_ratio_value(self) -> float:
        """Return the blockage ratio alpha = A_rotor / A_tunnel for this setup."""
        return self._blockage
