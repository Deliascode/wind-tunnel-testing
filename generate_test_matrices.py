"""
Entry point: generate the Task-1 and Task-2 Excel test matrices for Group 2.

Run with:
    python generate_test_matrices.py

It performs the full pipeline:
    1. Load the G1 look-up table (Re = 75000 slice) and read the rotor geometry.
    2. Build the Group-2 campaign configuration (tunnel, targets, constraints).
    3. Assemble the physics solver (air properties, blockage, Reynolds calibrator).
    4. Build the Task-1 (30 rows) and Task-2 (70 rows) matrices.
    5. Write each matrix to its own .xlsx file.
    6. Print a verification report against the Group-2 constraints.

No fallbacks: every value comes from the configuration or the look-up table; a
missing input or an out-of-range request raises immediately.
"""

from __future__ import annotations

from wtt.air_properties import AirProperties
from wtt.campaign_config import build_group2_campaign
from wtt.constraints import check_row
from wtt.excel_writer import TestMatrixExcelWriter
from wtt.lookup_table import G1LookUpTable
from wtt.operating_point import OperatingPointSolver
from wtt.reynolds_calibration import ReynoldsCalibrator
from wtt.scaling import samsung_s7_reference
from wtt.scaling_report import ScalingReport
from wtt.task1_builder import Task1PerformanceBuilder
from wtt.task2_builder import Task2WakeBuilder
from wtt.traverse_writer import TraversePositionWriter
from wtt.yaw_model import YawPerformanceModel


# File names.
LOOKUP_TABLE_PATH = "LookUpTable_G1.mat"
TASK1_OUTPUT = "Task1_Performance_TestMatrix_Group2.xlsx"
TASK2_OUTPUT = "Task2_Wake_TestMatrix_Group2.xlsx"
# Per-yaw wake traverse-position files (Lecture 5 p.21 format). One file per yaw
# because the survey positions shift with the wake center; A (probe angle) = 0.
TRAVERSE_OUTPUT_TEMPLATE = "Task2_Wake_TraversePositions_Group2_{label}.txt"

# Speed search interval for the Reynolds calibration root find [m/s].
# Wide enough to bracket the solution for every TSR in the sweep; if the target
# Reynolds cannot be reached inside this interval the solver raises on purpose.
SPEED_SEARCH_MIN = 0.5  # [m/s]
SPEED_SEARCH_MAX = 30.0  # [m/s]


def _yaw_label(yaw_deg: float) -> str:
    """Filename-safe label for a yaw angle (e.g. +30 -> 'yawPlus30')."""
    rounded = round(yaw_deg)
    if rounded > 0:
        return f"yawPlus{rounded}"
    if rounded < 0:
        return f"yawMinus{abs(rounded)}"
    return "yaw0"


def build_solver(config, lookup_table: G1LookUpTable) -> OperatingPointSolver:
    """Assemble the operating-point solver from the configuration and table."""
    air = AirProperties.at_reference_conditions()

    calibrator = ReynoldsCalibrator(
        tip_radius=lookup_table.tip_radius(),
        midspan_radius=lookup_table.midspan_radius(),
        midspan_chord=lookup_table.midspan_chord(),
        kinematic_viscosity=air.kinematic_viscosity,
        search_speed_min=SPEED_SEARCH_MIN,
        search_speed_max=SPEED_SEARCH_MAX,
    )

    yaw_model = YawPerformanceModel(
        power_cosine_exponent=config.yaw_model.power_cosine_exponent,
        thrust_cosine_exponent=config.yaw_model.thrust_cosine_exponent,
        rotational_asymmetry=config.yaw_model.rotational_asymmetry,
    )

    return OperatingPointSolver(
        lookup_table=lookup_table,
        air=air,
        tunnel_cross_section_area=config.tunnel.cross_section_area(),
        reynolds_calibrator=calibrator,
        yaw_model=yaw_model,
    )


def report_constraints(title, results, config, enforce_reynolds: bool) -> None:
    """Print any constraint violations for a set of operating-point results."""
    print(f"\n=== Constraint check: {title} ===")
    any_violation = False
    for index, result in enumerate(results, start=1):
        violations = check_row(
            result=result,
            constraints=config.constraints,
            target_reynolds=config.targets.target_reynolds,
            enforce_reynolds=enforce_reynolds,
        )
        if violations:
            any_violation = True
            print(f"  Row {index} (yaw={result.yaw_deg:+.0f}, TSR={result.tsr:.2f}):")
            for message in violations:
                print(f"      - {message}")
    if not any_violation:
        print("  All rows satisfy the Group-2 constraints.")


def print_summary(config, lookup_table: G1LookUpTable, solver: OperatingPointSolver) -> None:
    """Print a short summary of the key derived quantities."""
    optimum = lookup_table.optimum_operating_point()
    print("=== Campaign summary (Group 2) ===")
    print(f"  Rotor diameter           : {lookup_table.rotor_diameter():.4f} m")
    print(f"  Tip radius               : {lookup_table.tip_radius():.4f} m")
    print(f"  Midspan radius (r/R=0.5) : {lookup_table.midspan_radius():.4f} m")
    print(f"  Midspan chord            : {lookup_table.midspan_chord():.4f} m")
    print(f"  Tunnel cross-section area: {config.tunnel.cross_section_area():.4f} m^2")
    print(f"  Blockage ratio alpha     : {solver.blockage_ratio_value() * 100:.2f} %")
    print(
        f"  Table optimum            : Cp={optimum.cp:.4f} at "
        f"TSR={optimum.tsr:.3f}, pitch={optimum.pitch_deg:.2f} deg"
    )
    print(f"  Target Reynolds          : {config.targets.target_reynolds:.0f}")
    print(f"  Target TSR               : {config.targets.target_tsr:.3f}")
    traverse_x_mm = (
        config.wake.downstream_distance - config.traverse_home_offset
    ) * 1000.0
    print(
        f"  Wake station X = 2D      : {config.wake.downstream_distance:.4f} m "
        f"(traverse X = {traverse_x_mm:.0f} mm)"
    )
    print(f"  Wake requested speed     : {config.wake.requested_tunnel_speed:.2f} m/s")


def main() -> None:
    """Run the full generation pipeline."""
    # 1. Look-up table and geometry.
    lookup_table = G1LookUpTable(LOOKUP_TABLE_PATH)
    rotor_diameter = lookup_table.rotor_diameter()

    # 2. Configuration.
    config = build_group2_campaign(
        lookup_table_path=LOOKUP_TABLE_PATH,
        rotor_diameter=rotor_diameter,
    )

    # 3. Solver.
    solver = build_solver(config, lookup_table)
    print_summary(config, lookup_table, solver)

    # Scaling report: relate the G1 model to its full-scale reference using the
    # representative (optimum) operating rotor speed for the time scale.
    optimum = lookup_table.optimum_operating_point()
    optimum_rpm = solver.solve_for_fixed_tunnel_speed(
        tsr=optimum.tsr,
        pitch_deg=config.targets.optimum_pitch_deg,
        yaw_deg=0.0,
        tunnel_speed=config.wake.requested_tunnel_speed,
    ).rotor_speed_rpm
    scaling_report = ScalingReport(
        full_scale=samsung_s7_reference(),
        model_rotor_diameter=config.rotor_diameter,
        model_rotor_speed_rpm=optimum_rpm,
    )
    scaling_rows = scaling_report.rows()
    print("\n=== Scaling factors (model / full-scale, Samsung S7.0-171) ===")
    print(f"  n_L = {scaling_report.length_scale_value():.5g}, "
          f"n_T = {scaling_report.time_scale_value():.5g}")
    for factor in scaling_rows:
        print(f"  {factor.quantity:18} {factor.combination:14} = {factor.value:.4g}")

    # 4. Task 1 (performance, requested-speed grid at constant Re).
    task1_builder = Task1PerformanceBuilder(config, solver)
    task1_results = task1_builder.build_results()
    task1_rows = task1_builder.build_rows()

    # 5. Task 2 (wake, y-z plane, 69 rows).
    task2_builder = Task2WakeBuilder(config, solver)
    task2_results = [result for result, _positions in task2_builder.build_results()]
    task2_rows = task2_builder.build_rows()

    # 6. Write Excel files.
    TestMatrixExcelWriter(include_wake_position=False).write(
        rows=task1_rows,
        sheet_title="Task1 Performance G2",
        file_path=TASK1_OUTPUT,
        scaling_rows=scaling_rows,
    )
    TestMatrixExcelWriter(include_wake_position=True).write(
        rows=task2_rows,
        sheet_title="Task2 Wake G2",
        file_path=TASK2_OUTPUT,
        scaling_rows=scaling_rows,
    )
    print(f"\nWrote {len(task1_rows)} rows -> {TASK1_OUTPUT}")
    print(f"Wrote {len(task2_rows)} rows -> {TASK2_OUTPUT}")

    # 6b. Wake traverse-position files: one per yaw, A (probe angle) = 0 throughout.
    traverse_writer = TraversePositionWriter()
    for yaw_deg, positions in task2_builder.traverse_blocks():
        path = TRAVERSE_OUTPUT_TEMPLATE.format(label=_yaw_label(yaw_deg))
        traverse_writer.write(file_path=path, positions=positions)
        print(f"Wrote {len(positions)} traverse points -> {path}")

    # 7. Verify constraints (Reynolds enforced only for the performance task).
    report_constraints("Task 1 (performance)", task1_results, config, enforce_reynolds=True)
    report_constraints("Task 2 (wake)", task2_results, config, enforce_reynolds=False)


if __name__ == "__main__":
    main()
