"""Task 1 performance test matrix for Group 2.

Generated from:
Task1_Performance_TestMatrix_Group2_measurements.xlsx
Sheet: Task1 Performance G2
"""

from __future__ import annotations

from typing import Any

COLUMNS: list[str] = ['Test number', 'Requested wind speed [m/s]', "Equivalent free-air U' [m/s]", 'Blade pitch [deg]', 'Rotor speed [rpm]', 'Yaw [deg]', 'Reynolds [-]', 'TSR [-]', 'Expected C_P [-]', 'Expected C_T (thrust) [-]', 'Expected Power [W]', 'Expected Torque [Nm]', 'Expected Thrust [N]', 'Meas. Rotor azimuth [deg]', 'Meas. Rotor speed [rpm]', 'Meas. Generator torque [Nm]', 'Meas. Aerodynamic torque [Nm]', 'Meas. Tower fore-aft moment [Nm]', 'Meas. Tower side-side moment [Nm]', 'Meas. Shaft bending moment [Nm]', 'Meas. Demanded pitch B1 [deg]', 'Meas. Actual pitch B1 [deg]', 'Meas. Demanded pitch B2 [deg]', 'Meas. Actual pitch B2 [deg]', 'Meas. Demanded pitch B3 [deg]', 'Meas. Actual pitch B3 [deg]', 'Meas. Demanded yaw [deg]', 'Meas. Actual yaw [deg]', 'Top', 'File number']

ROWS: list[list[Any]] = [[1, 4, 4.921333131788917, 0.4, 708.9058338978167, -30, 70857.34728718578, 8.2, 0.2424417161663958, 0.6174191787971431, 16.15070460440171, 0.2175576232522368, 8.357597969083072, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 1, 5], [2, 4, 4.921333131788917, 0.4, 708.9058338978167, 0, 70857.34728718578, 8.2, 0.3755534, 0.8282760353597667, 25.01818631912255, 0.3370067923963221, 11.21182876834048, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 2, 5], [3, 4, 4.921333131788917, 0.4, 708.9058338978167, 30, 70857.34728718578, 8.2, 0.2454164611500326, 0.624994874242507, 16.34887275905694, 0.2202270419424483, 8.46014518342765, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 3, 5], [4, 4, 5.01343028955351, 0.4, 748.5931352811393, -30, 74726.78980723246, 8.5, 0.2328195841105167, 0.627342994099444, 16.39684469328276, 0.2091634636536704, 8.812737735189458, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 5, 5], [5, 4, 5.01343028955351, 0.4, 748.5931352811393, 0, 74726.78980723246, 8.5, 0.3605702, 0.8414067770959012, 25.39397015510277, 0.3239337112057403, 11.81984548309434, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 6, 5], [6, 4, 5.01343028955351, 0.4, 748.5931352811393, 30, 74726.78980723246, 8.5, 0.235574845460937, 0.6347671715444079, 16.59089019261155, 0.2116387709158441, 8.917030489452056, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 7, 5], [7, 4, 5.062106647046976, 0.4, 782.5388299068021, -30, 78034.30212239618, 8.8, 0.2215101694598935, 0.6320635886123881, 16.05918026937516, 0.1959696687904388, 9.052305160614017, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 8, 5], [8, 4, 5.062106647046976, 0.4, 782.5388299068021, 0, 78034.30212239618, 8.8, 0.342986, 0.8475671740630879, 24.86600961618242, 0.3034391287029706, 12.13871015823289, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 9, 5], [9, 4, 5.062106647046976, 0.4, 782.5388299068021, 30, 78034.30212239618, 8.8, 0.2240417142537208, 0.639287172482244, 16.24271375816802, 0.1982093221480438, 9.15576007673532, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 10, 5], [10, 4.5, 5.312931013957924, 0.4, 709.3159130408453, -30, 71133.65539085743, 7.6, 0.2569838917494583, 0.5892898752092429, 21.53992885844746, 0.2899852735833607, 9.296793090335878, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 11, 5], [11, 4.5, 5.312931013957924, 0.4, 709.3159130408453, 0, 71133.65539085743, 7.6, 0.3982728, 0.7909232762190279, 33.38251172030029, 0.4494182342814276, 12.47781500866272, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 12, 5], [12, 4.5, 5.312931013957924, 0.4, 709.3159130408453, 30, 71133.65539085743, 7.6, 0.2603876519050803, 0.5970950391192992, 21.82522592942027, 0.2938261381341336, 9.419929422658209, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 13, 5], [13, 4.5, 5.418230401732103, 0.4, 751.928410027258, -30, 75274.7317075722, 7.9, 0.2507082883809472, 0.603917710048243, 22.28829927565436, 0.2830556437709257, 9.908970500693044, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 14, 5], [14, 4.5, 5.418230401732103, 0.4, 751.928410027258, 0, 75274.7317075722, 7.9, 0.3884492000000001, 0.8103524262218462, 34.53364896270609, 0.4385684218434361, 13.29611328330786, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 15, 5], [15, 4.5, 5.418230401732103, 0.4, 751.928410027258, 30, 75274.7317075722, 7.9, 0.2539020245386662, 0.6116109292845264, 22.57222665496205, 0.2866614481501731, 10.03519942426875, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 16, 5], [16, 4.5, 5.536499773262532, 0.4, 797.5190631350439, -30, 79714.515698084, 8.2, 0.2424417161663958, 0.6174191787971431, 22.99582745431415, 0.2753463669286122, 10.57758492962076, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 17, 5], [17, 4.5, 5.536499773262532, 0.4, 797.5190631350439, 0, 79714.515698084, 8.2, 0.3755534, 0.8282760353597667, 35.62159731765692, 0.4265242216265951, 14.18997078493092, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 18, 5], [18, 4.5, 5.536499773262532, 0.4, 797.5190631350439, 30, 79714.515698084, 8.2, 0.2454164611500326, 0.624994874242507, 23.27798484639163, 0.2787248499584111, 10.70737124777562, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 19, 5], [19, 5, 5.757932521134195, 0.4, 708.0379645801992, -30, 71280.42089702174, 7, 0.2613071611331977, 0.5662553961487662, 27.87962044461324, 0.3760119903669485, 10.49255677654289, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 20, 5], [20, 5, 5.757932521134195, 0.4, 708.0379645801992, 0, 71280.42089702174, 7, 0.405203, 0.7604389013028994, 43.23228569025009, 0.5830731384165727, 14.09072372869069, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 21, 5], [21, 5, 5.757932521134195, 0.4, 708.0379645801992, 30, 71280.42089702174, 7, 0.2650669764013012, 0.574402955805583, 28.28076606252134, 0.38142223483266, 10.64352881649314, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 22, 5], [22, 5, 5.82680094756339, 0.4, 747.213958552533, -30, 75071.72548692921, 7.3, 0.2614334429535168, 0.5779554820989141, 28.9059682473507, 0.3694144906234211, 10.96706921092968, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 23, 5], [23, 5, 5.82680094756339, 0.4, 747.213958552533, 0, 75071.72548692921, 7.3, 0.405279, 0.7759218426339445, 44.81057118389013, 0.5726732343573548, 14.72360556134008, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 24, 5], [24, 5, 5.82680094756339, 0.4, 747.213958552533, 30, 75071.72548692921, 7.3, 0.2650394214770136, 0.5859272818520027, 29.30467125765899, 0.3745098629078821, 11.11833913108044, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 25, 5], [25, 5, 5.903256682175472, 0.4, 788.128792267606, -30, 79037.39487873051, 7.6, 0.2569838917494583, 0.5892898752092429, 29.5472275150171, 0.3580065105967415, 11.477522333748, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 26, 5], [26, 5, 5.903256682175472, 0.4, 788.128792267606, 0, 79037.39487873051, 7.6, 0.3982728, 0.7909232762190279, 45.79219714718833, 0.5548373262733673, 15.40470988723793, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 27, 5], [27, 5, 5.903256682175472, 0.4, 788.128792267606, 30, 79037.39487873051, 7.6, 0.2603876519050803, 0.5970950391192992, 29.93858152183851, 0.3627483186841156, 11.6295424971089, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 28, 5], [28, 5.5, 6.151783942567948, 0.4, 691.6286610458543, -30, 70003.61510190072, 6.4, 0.2523400498411734, 0.5304042160859316, 32.83410928309335, 0.4533395813749253, 11.21876234642389, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 29, 5], [29, 5.5, 6.151783942567948, 0.4, 691.6286610458543, 0, 70003.61510190072, 6.4, 0.391562, 0.7127741696482859, 50.94946088501897, 0.703457708255413, 15.07613207708407, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 30, 5], [30, 5.5, 6.151783942567948, 0.4, 691.6286610458543, 30, 70003.61510190072, 6.4, 0.2563139088937902, 0.5387570383864975, 33.35118187022869, 0.4604787873808297, 11.39543576920222, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 31, 5]]


def as_records() -> list[dict[str, Any]]:
    """Return the test matrix as one dictionary per test."""
    return [dict(zip(COLUMNS, row, strict=True)) for row in ROWS]


def print_table() -> None:
    """Print a readable table without requiring external packages."""
    records = as_records()
    selected = [
        "Test number",
        "Requested wind speed [m/s]",
        "Equivalent free-air U' [m/s]",
        "Blade pitch [deg]",
        "Rotor speed [rpm]",
        "Yaw [deg]",
        "Reynolds [-]",
        "TSR [-]",
        "Expected C_P [-]",
        "Expected C_T (thrust) [-]",
        "Expected Power [W]",
        "Expected Torque [Nm]",
        "Expected Thrust [N]",
        "Top",
        "File number",
    ]

    widths = {
        column: max(len(column), *(len(str(record[column])) for record in records))
        for column in selected
    }

    print(" | ".join(column.ljust(widths[column]) for column in selected))
    print("-+-".join("-" * widths[column] for column in selected))
    for record in records:
        print(" | ".join(str(record[column]).ljust(widths[column]) for column in selected))

import tkinter as tk
from tkinter import ttk


def _display_value(value: Any) -> str:
    """Format values for display in the table."""
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def show_table_window() -> None:
    """Open the complete test matrix in a separate scrollable window."""
    window = tk.Tk()
    window.title("Task 1 Performance Test Matrix – Group 2")
    window.geometry("1500x750")
    window.minsize(900, 500)

    container = ttk.Frame(window, padding=8)
    container.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        container,
        columns=COLUMNS,
        show="headings",
        selectmode="browse",
    )

    vertical_scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=tree.yview,
    )
    horizontal_scrollbar = ttk.Scrollbar(
        container,
        orient="horizontal",
        command=tree.xview,
    )

    tree.configure(
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set,
    )

    tree.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    for column in COLUMNS:
        width = max(120, min(230, len(column) * 8))
        tree.heading(column, text=column)
        tree.column(column, width=width, minwidth=80, anchor="center", stretch=False)

    for row in ROWS:
        tree.insert(
            "",
            "end",
            values=[_display_value(value) for value in row],
        )

    close_button = ttk.Button(window, text="Close", command=window.destroy)
    close_button.pack(pady=(0, 8))

    window.mainloop()


if __name__ == "__main__":
    show_table_window()
