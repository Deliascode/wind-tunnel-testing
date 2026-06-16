"""
Writer for the wake-traverse position files (Task 2).

The probe-traversing system is fed a tab-separated .txt file of X/Y/Z/A positions
(Lecture 5, slide 21 format). One file is written per turbine-yaw case, because
the wake center -- and therefore the survey positions -- shifts with yaw, while
the probe angle A is always 0 (the probe is never angled).

Coordinate frame: traverse coordinates in millimetres; home X/Y/Z = 0 sits at hub
height, 0.5 D behind the rotor (see `Task2WakeBuilder`).
"""

from __future__ import annotations


class TraversePositionWriter:
    """Writes tab-separated X/Y/Z/A traverse-position files."""

    # Tab-separated header expected by the traversing system (Lecture 5, p.21).
    _HEADER: tuple[str, ...] = ("x", "y", "z", "A")

    def write(
        self,
        file_path: str,
        positions: list[tuple[float, float, float, float]],
    ) -> None:
        """
        Write one traverse file: a header line plus one TAB-separated row per point.

        `positions` is a list of (X, Y, Z, A) tuples in millimetres / degrees. X/Y/Z
        are written with one decimal; A (always 0) as an integer.
        """
        lines = ["\t".join(self._HEADER)]
        for x_mm, y_mm, z_mm, a_deg in positions:
            lines.append(f"{x_mm:.1f}\t{y_mm:.1f}\t{z_mm:.1f}\t{a_deg:.0f}")
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
