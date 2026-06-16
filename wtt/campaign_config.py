"""
Configuration objects for the G1 wind-tunnel test campaign.

These are plain immutable data containers (frozen dataclasses) that hold the
fixed facts of the experiment: the wind-tunnel geometry, the operating targets
(Reynolds number, target TSR, optimum pitch), the Group-2 constraints, and the
wake-survey settings.

NOTE on the "no defaults" rule: the dataclasses below intentionally do NOT give
default values to physically meaningful quantities. The concrete numbers for the
actual campaign live in `build_group2_campaign()` at the bottom, in ONE place,
so they are easy to find and change. If you forget to pass one, construction
fails on purpose.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WindTunnelGeometry:
    """
    Test-section geometry of the wind tunnel.

    The blockage correction only needs the cross-sectional area that the flow
    passes through (height x width). The length is kept for documentation and
    for sanity-checking the downstream measurement positions.
    """

    length: float  # [m]  streamwise length of the test section
    width: float  # [m]   horizontal (cross-stream) width
    height: float  # [m]  vertical height

    def cross_section_area(self) -> float:
        """Cross-sectional area seen by the flow: width * height (single formula)."""
        return self.width * self.height


@dataclass(frozen=True)
class OperatingTargets:
    """Targets that define the desired operating point of the rotor."""

    target_reynolds: float  # [-]  Reynolds number to calibrate to (75000)
    target_tsr: float  # [-]       tip-speed ratio to set at the design point (7.05)
    optimum_pitch_deg: float  # [deg] collective blade pitch (0 now, changeable)


@dataclass(frozen=True)
class Group2Constraints:
    """Hard limits the test matrix must respect (Group 2)."""

    tsr_min: float  # [-]
    tsr_max: float  # [-]
    power_max_w: float  # [W]
    torque_max_nm: float  # [Nm]
    rotor_speed_max_rpm: float  # [rpm]
    reynolds_tolerance: float  # [-] allowed +/- band around target Reynolds


@dataclass(frozen=True)
class WakeSurveySettings:
    """
    Settings for the Task-2 wake survey.

    The survey now samples a full y-z plane at a single downstream station: a
    horizontal hub-height line (Z = 0) plus one or more concentric circles in the
    plane so the wake can be graphed and the center best-fitted.
    """

    requested_tunnel_speed: float  # [m/s] speed COMMANDED on the tunnel (5.4); the
    #                                rotor feels U' = this * Glauert factor (blockage).
    downstream_distance: float  # [m]    streamwise station X = 2D behind the rotor
    wake_expansion_coefficient: float  # [-] Jimenez k_d
    hubline_points: int  # [-]          points on the Y axis (Z = 0), per yaw
    ring_point_counts: tuple[int, ...]  # [-] points on each concentric circle (even)
    ring_radius_fractions: tuple[float, ...]  # [-] circle radius / reachable radius
    span_factor: float  # [-]           Y-line half-width = span_factor * wake radius
    # Traverse limits of the wake probe (from the lecture), in metres.
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float


@dataclass(frozen=True)
class YawSchedule:
    """The set of yaw misalignment angles to test (Group 2: 0, +30, -30)."""

    yaw_angles_deg: tuple[float, ...]


@dataclass(frozen=True)
class YawModelSettings:
    """
    Parameters of the yaw-dependent performance correction (see `wtt.yaw_model`).

    The cosine exponents follow from actuator-disk momentum theory applied to the
    rotor-normal wind component U cos(gamma): power scales with cos^3 and thrust
    with cos^2. `rotational_asymmetry` (k_gamma) scales the advancing/retreating-
    blade coupling that makes +gamma and -gamma differ for a fixed rotation sense;
    its sign and magnitude are modelling parameters to be calibrated against
    measurement (no hidden default — it must be set explicitly here).
    """

    power_cosine_exponent: float  # [-]  p_P (momentum theory: 3)
    thrust_cosine_exponent: float  # [-] p_T (momentum theory: 2)
    rotational_asymmetry: float  # [-]   k_gamma sensitivity (calibrate to data)


@dataclass(frozen=True)
class CampaignConfig:
    """Top-level container grouping every configuration block for one campaign."""

    tunnel: WindTunnelGeometry
    targets: OperatingTargets
    constraints: Group2Constraints
    wake: WakeSurveySettings
    yaw: YawSchedule
    yaw_model: YawModelSettings
    lookup_table_path: str
    rotor_diameter: float  # [m]  aerodynamic G1 rotor diameter (from the lookup geometry)
    # Nominal traverse-grid diameter: the wake-traverse coordinate system uses the
    # round figure 1D = 1100 mm (Lecture 5), independent of the slightly different
    # aerodynamic diameter that drives the wake physics. Probe positions are placed
    # on this nominal grid; the Jimenez wake model still uses `rotor_diameter`.
    nominal_rotor_diameter: float  # [m]  1D for the traverse grid (1.1)
    traverse_home_offset: float  # [m]    home X is this far behind the rotor (0.5 D_nom)
    performance_speed_step: float  # [m/s] requested-speed grid step for Task 1 (0.5)


def build_group2_campaign(
    lookup_table_path: str,
    rotor_diameter: float,
) -> CampaignConfig:
    """
    Assemble the concrete configuration for the Group-2 campaign.

    This is the single place where the campaign numbers are written down. The
    rotor diameter is passed in (it is read from the lookup-table geometry, so we
    do not hard-code it here) which keeps geometry and configuration consistent.
    """
    # Nominal traverse-grid diameter and home offset (Lecture 5): the probe-
    # traversing coordinate system uses 1D = 1100 mm and a home position 0.5D
    # behind the rotor. These are deliberately the round grid figures, not the
    # aerodynamic diameter.
    nominal_diameter = 1.1  # [m]  1D = 1100 mm
    home_offset = 0.5 * nominal_diameter  # [m]  home is 0.5D behind the rotor
    return CampaignConfig(
        tunnel=WindTunnelGeometry(
            length=4.5,  # [m]
            width=2.7,  # [m]
            height=1.8,  # [m]
        ),
        targets=OperatingTargets(
            target_reynolds=75000.0,
            target_tsr=7.05,
            optimum_pitch_deg=0.4,  # [deg]  small positive pitch
        ),
        constraints=Group2Constraints(
            tsr_min=5.5,
            tsr_max=9.0,
            power_max_w=75.0,
            torque_max_nm=1.0,
            rotor_speed_max_rpm=850.0,
            reynolds_tolerance=2000.0,
        ),
        wake=WakeSurveySettings(
            requested_tunnel_speed=5.4,  # [m/s] commanded tunnel speed for Group 2
            downstream_distance=2.0 * nominal_diameter,  # X = 2D behind the rotor
            wake_expansion_coefficient=0.07,
            hubline_points=9,  # 9 points kept on the Y axis (Z = 0)
            ring_point_counts=(6, 8),  # small + big concentric circle (even counts)
            ring_radius_fractions=(0.45, 0.85),  # of the reachable in-plane radius
            span_factor=1.5,  # Y-line half-width = 1.5 * wake radius (fit to limits)
            # Traverse limits from Lecture 5 (converted mm -> m).
            x_min=0.0,
            x_max=3.850,
            y_min=-1.0,
            y_max=1.0,
            z_min=-0.7,
            z_max=0.6,
        ),
        yaw=YawSchedule(
            yaw_angles_deg=(0.0, 30.0, -30.0),
        ),
        yaw_model=YawModelSettings(
            # Momentum-theory cosine exponents (rotor-normal wind U cos gamma):
            # power ~ cos^3, thrust ~ cos^2 (Lecture 3 actuator-disk theory).
            power_cosine_exponent=3.0,
            thrust_cosine_exponent=2.0,
            # Rotational +/- yaw asymmetry sensitivity (advance-ratio coupling).
            # Nominal small value; sign/magnitude to be calibrated against the
            # measured yaw sweep. Set to 0.0 to recover a symmetric cosine law.
            rotational_asymmetry=0.10,
        ),
        lookup_table_path=lookup_table_path,
        rotor_diameter=rotor_diameter,
        nominal_rotor_diameter=nominal_diameter,
        traverse_home_offset=home_offset,
        performance_speed_step=0.5,  # [m/s] requested-speed grid step (Task 1)
    )
