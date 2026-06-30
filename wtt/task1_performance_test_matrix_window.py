from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd


# Projektstruktur:
#
# wind-tunnel-testing/
# ├── data/
# │   └── Task1_Performance_TestMatrix_Group2_measurements.xlsx
# └── wtt/
#     └── task1_performance_test_matrix_window.py


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "Task1_Performance_TestMatrix_Group2_measurements.xlsx"
)

SHEET_NAME = "Task1 Performance G2"


def load_excel_table() -> pd.DataFrame:
    """Read the performance test matrix from the Excel file."""

    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            "Die Excel-Datei wurde nicht gefunden.\n\n"
            f"Erwarteter Speicherort:\n{EXCEL_PATH}"
        )

    dataframe = pd.read_excel(
        EXCEL_PATH,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    # Vollständig leere Zeilen und Spalten entfernen
    dataframe = dataframe.dropna(axis=0, how="all")
    dataframe = dataframe.dropna(axis=1, how="all")

    return dataframe


def format_value(value: object) -> str:
    """Format table values for display."""

    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.6g}"

    return str(value)


def show_table_window(dataframe: pd.DataFrame) -> None:
    """Display the Excel table in a separate scrollable window."""

    window = tk.Tk()
    window.title("Task 1 Performance Test Matrix – Group 2")
    window.geometry("1500x750")
    window.minsize(900, 500)

    main_frame = ttk.Frame(window, padding=10)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(
        main_frame,
        text="Task 1 Performance Test Matrix – Group 2",
        font=("Segoe UI", 14, "bold"),
    )
    title_label.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(0, 10),
    )

    columns = [str(column) for column in dataframe.columns]

    tree = ttk.Treeview(
        main_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )

    vertical_scrollbar = ttk.Scrollbar(
        main_frame,
        orient="vertical",
        command=tree.yview,
    )

    horizontal_scrollbar = ttk.Scrollbar(
        main_frame,
        orient="horizontal",
        command=tree.xview,
    )

    tree.configure(
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set,
    )

    tree.grid(
        row=1,
        column=0,
        sticky="nsew",
    )

    vertical_scrollbar.grid(
        row=1,
        column=1,
        sticky="ns",
    )

    horizontal_scrollbar.grid(
        row=2,
        column=0,
        sticky="ew",
    )

    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)

    for column in columns:
        column_width = max(
            120,
            min(250, len(column) * 8),
        )

        tree.heading(
            column,
            text=column,
        )

        tree.column(
            column,
            width=column_width,
            minwidth=80,
            anchor="center",
            stretch=False,
        )

    for row in dataframe.itertuples(index=False, name=None):
        formatted_row = [
            format_value(value)
            for value in row
        ]

        tree.insert(
            "",
            "end",
            values=formatted_row,
        )

    status_label = ttk.Label(
        main_frame,
        text=(
            f"{len(dataframe)} rows | "
            f"{len(dataframe.columns)} columns | "
            f"File: {EXCEL_PATH.name}"
        ),
    )

    status_label.grid(
        row=3,
        column=0,
        sticky="w",
        pady=(8, 0),
    )

    close_button = ttk.Button(
        main_frame,
        text="Close",
        command=window.destroy,
    )

    close_button.grid(
        row=3,
        column=1,
        sticky="e",
        pady=(8, 0),
    )

    window.mainloop()


def main() -> None:
    """Load the Excel file and open the table window."""

    try:
        dataframe = load_excel_table()

    except FileNotFoundError as error:
        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Excel file not found",
            str(error),
        )

        root.destroy()
        return

    except ValueError as error:
        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Worksheet error",
            "Das Excel-Tabellenblatt konnte nicht gefunden werden.\n\n"
            f"Erwarteter Tabellenblattname:\n{SHEET_NAME}\n\n"
            f"Fehlermeldung:\n{error}",
        )

        root.destroy()
        return

    except Exception as error:
        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Error",
            "Beim Einlesen der Excel-Datei ist ein Fehler aufgetreten.\n\n"
            f"{type(error).__name__}: {error}",
        )

        root.destroy()
        return

    show_table_window(dataframe)


if __name__ == "__main__":
    main()