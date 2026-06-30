from pathlib import Path

source_path = Path("/mnt/data/task1_performance_test_matrix.py")
output_path = Path("/mnt/data/task1_performance_test_matrix_window.py")

text = source_path.read_text(encoding="utf-8")

# Remove the existing command-line entry point, then add a Tkinter window.
marker = '\nif __name__ == "__main__":\n    print_table()\n'
if marker in text:
    text = text.replace(marker, "\n")

gui_code = r'''
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
'''

output_path.write_text(text.rstrip() + "\n\n" + gui_code.lstrip(), encoding="utf-8")
print(f"Created: {output_path}")
