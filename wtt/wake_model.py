"""
Wake-center deflection and wake-survey point distribution for Task 2.

Physical picture (Lecture 3, "Wake Deflection by Yaw Misalignment", and the
Cacciola/Bottasso paper on wake-center tracking): when the turbine is yawed, the
wake is deflected laterally. To place the wake-probe points usefully we must
distribute them *around the expected wake center*, which shifts in the Y
(lateral) direction depending on the yaw angle and the downstream distance.

We use the classical Jimenez (2010) analytical wake-deflection model to predict
the lateral position of the wake center, and then build a hub-height line of Y
positions that is denser near that center and sparser towards the edges (the
paper shows the wake center is best resolved when points straddle it).

Reference frame (assignment): X is the downwind direction, Z points downwards,
origin at the hub center. Y is the remaining (lateral) horizontal axis. Wake
measurements are limited to hub height, i.e. Z = 0.

Each formula is its own function.
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------------------
# Jimenez wake-center deflection
# ---------------------------------------------------------------------------
def initial_skew_angle(thrust_coefficient: float, yaw_angle_rad: float) -> float:
    """
    Initial wake skew angle at the rotor plane (Jimenez):

        xi0 = 0.5 * cos^2(gamma) * sin(gamma) * C_T

    `gamma` is the yaw misalignment, `C_T` the rotor THRUST coefficient. The sign
    follows the sign of the yaw angle, so a positive yaw gives a positive skew.
    """
    return 0.5 * math.cos(yaw_angle_rad) ** 2 * math.sin(yaw_angle_rad) * thrust_coefficient


def wake_center_offset(
    thrust_coefficient: float,
    yaw_angle_rad: float,
    wake_expansion_coefficient: float,
    rotor_diameter: float,
    downstream_distance: float,
) -> float:
    """
    Lateral (Y) offset of the wake center at a downstream distance x.

    The local deflection angle decays as the wake expands,
        xi(x) = xi0 / (1 + 2 k_d x / D)^2 ,
    and the lateral offset is the integral of tan(xi) ~ xi along x, which has the
    closed form

        delta(x) = (xi0 * D / (2 k_d)) * (1 - 1 / (1 + 2 k_d x / D))

    Returns the offset in metres. At zero yaw xi0 = 0, so delta = 0.
    """
    xi0 = initial_skew_angle(thrust_coefficient, yaw_angle_rad)
    expansion = 1.0 + 2.0 * wake_expansion_coefficient * downstream_distance / rotor_diameter
    return (xi0 * rotor_diameter / (2.0 * wake_expansion_coefficient)) * (
        1.0 - 1.0 / expansion
    )


def wake_radius(
    wake_expansion_coefficient: float,
    rotor_diameter: float,
    downstream_distance: float,
) -> float:
    """
    Approximate wake radius at distance x: r_w = R + k_d * x.

    Used to size the lateral span over which the survey points are spread.
    """
    rotor_radius = rotor_diameter / 2.0
    return rotor_radius + wake_expansion_coefficient * downstream_distance


# ---------------------------------------------------------------------------
# Survey-point distribution (hub-height Y line centred on the wake center)
# ---------------------------------------------------------------------------
def centered_lateral_positions(
    wake_center_y: float,
    half_width: float,
    number_of_points: int,
) -> np.ndarray:
    """
    Build `number_of_points` Y positions centred on `wake_center_y`.

    Cosine spacing is used so that points cluster near the center (where the wake
    gradient is steepest and the center is best identified) and thin out towards
    the edges. The positions span [center - half_width, center + half_width].
    """
    if number_of_points < 2:
        raise ValueError("Need at least two lateral points to span the wake.")
    # Parameter t in [0, pi]; cos(t) gives endpoints at +/-1 with clustering at 0.
    t = np.linspace(0.0, math.pi, number_of_points)
    # -cos(t) maps to [-1, 1] increasing; multiply by half_width and shift.
    normalized = -np.cos(t)
    return wake_center_y + half_width * normalized


def clip_to_limits(values: np.ndarray, lower: float, upper: float) -> np.ndarray:
    """Clamp an array of positions into the allowed traverse range [lower, upper]."""
    return np.clip(values, lower, upper)


def fitted_half_width(
    wake_center_y: float,
    desired_half_width: float,
    lower_limit: float,
    upper_limit: float,
) -> float:
    """
    Largest symmetric half-width around `wake_center_y` that still fits the limits.

    The survey line is symmetric about the wake center, so the usable half-width
    is bounded by the nearer traverse wall:

        available = min(center - lower_limit, upper_limit - center)

    The returned value is min(desired_half_width, available), which guarantees the
    extreme points land exactly on (not beyond) the traverse limits, so no point
    has to be clipped and the cosine clustering is preserved. Raises if the center
    itself lies outside the limits (that would be a configuration error).
    """
    if not (lower_limit <= wake_center_y <= upper_limit):
        raise ValueError(
            f"Wake center {wake_center_y:.3f} m lies outside the traverse "
            f"limits [{lower_limit}, {upper_limit}] m."
        )
    available = min(wake_center_y - lower_limit, upper_limit - wake_center_y)
    return min(desired_half_width, available)


# ---------------------------------------------------------------------------
# In-plane (y-z) concentric-circle distribution
# ---------------------------------------------------------------------------
def reachable_radius(
    wake_center_y: float,
    y_min: float,
    y_max: float,
    z_min: float,
    z_max: float,
) -> float:
    """
    Largest in-plane circle radius (centred on the wake center) that fits the box.

    A survey circle is centred at (Y = wake_center_y, Z = 0). Its nearest approach
    to each traverse wall caps the radius:

        horizontal = min(center - y_min, y_max - center)
        vertical   = min(z_max, -z_min)        # Z = 0 is hub height

    The reachable radius is the smaller of the two. Raises if the center already
    lies outside the Y limits (a configuration error).
    """
    if not (y_min <= wake_center_y <= y_max):
        raise ValueError(
            f"Wake center {wake_center_y:.3f} m lies outside the Y traverse "
            f"limits [{y_min}, {y_max}] m."
        )
    horizontal = min(wake_center_y - y_min, y_max - wake_center_y)
    vertical = min(z_max, -z_min)
    return min(horizontal, vertical)


def concentric_ring_positions(
    wake_center_y: float,
    radius: float,
    number_of_points: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    (Y, Z) coordinates of `number_of_points` points equally spaced on a circle.

    The circle is centred at (Y = wake_center_y, Z = 0). The angular grid is
    offset by half a step,

        theta_k = (2k + 1) * pi / n ,    k = 0 .. n - 1 ,

    so that for an EVEN number of points none of them falls on Z = 0 (the
    hub-height Y axis). This keeps the dedicated Y-axis points distinct from the
    circle points, as required. An odd count would place one point on the axis and
    is therefore rejected (fail-fast).

    Returns two arrays (Y, Z) in metres.
    """
    if number_of_points < 2:
        raise ValueError("Need at least two points to define a circle.")
    if number_of_points % 2 != 0:
        raise ValueError(
            "Ring point count must be even so no circle point lands on the Z = 0 axis."
        )
    k = np.arange(number_of_points)
    theta = (2.0 * k + 1.0) * math.pi / number_of_points
    y_positions = wake_center_y + radius * np.cos(theta)
    z_positions = radius * np.sin(theta)
    return y_positions, z_positions
