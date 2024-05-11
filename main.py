import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, IntVar

from PIL import ImageTk, Image
from PIL.Image import Resampling

from config import apply_style, load_config
from interactive_map import generate_interactive_map
from reports import load_data, generate_charts, create_pdf_report

APP_VERSION = "BETA V0.1.9"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChartSelectionDialog(tk.Toplevel):
    def __init__(self, parent, columns, callback):
        super().__init__(parent)
        self.title("Select Chart Types")
        self.geometry("400x400")
        self.chart_type_vars = {}
        self.callback = callback
        chart_types = ['Pie Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        frame = ttk.Frame(self)
        frame.pack(pady=10, padx=10, fill='both', expand=True)
        for column in columns:
            var = tk.StringVar(value='Pie Chart')
            row_frame = ttk.Frame(frame)
            row_frame.pack(anchor='w', fill='x')
            ttk.Label(row_frame, text=column).pack(side='left', padx=10)
            chart_type_menu = ttk.Combobox(row_frame, textvariable=var, values=chart_types, state='readonly')
            chart_type_menu.pack(side='left')
            self.chart_type_vars[column] = var
        ttk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

    def on_ok(self):
        column_chart_pairs = [(column, var.get()) for column, var in self.chart_type_vars.items()]
        self.callback(column_chart_pairs)
        self.destroy()

class App:
    def __init__(self, root):
        self.root = root
        self.df = None
        self.columns = []
        self.column_vars = {}
        self.output_folder = ""
        self.config = load_config()
        self.latitude_col = None
        self.longitude_col = None
        self.column_chart_pairs = []
        root.title('Report Generator')
        root.geometry("750x600")
        apply_style(root)  # Apply the custom style

        top_frame = ttk.Frame(root)
        top_frame.pack(pady=10, padx=10, fill='x')
        middle_frame = ttk.Frame(root)
        middle_frame.pack(pady=10, padx=10, fill='both', expand=True)
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(pady=10, padx=10, fill='x')

        logo_path = os.path.join(sys._MEIPASS, "images", "icon_app.png") if getattr(sys, 'frozen', False) else "images/icon_app.png"
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((50, 50), Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ttk.Label(top_frame, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side='left')

        ttk.Button(top_frame, text="Open Excel File", command=self.open_file).pack(side='left', padx=10)
        ttk.Button(top_frame, text="Select Output Folder", command=self.select_output_folder).pack(side='left', padx=10)

        self.columns_canvas = tk.Canvas(middle_frame)
        self.columns_frame = ttk.Frame(self.columns_canvas)
        self.vsb = ttk.Scrollbar(middle_frame, orient="vertical", command=self.columns_canvas.yview)
        self.columns_canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_canvas.create_window((4, 4), window=self.columns_frame, anchor="nw", tags="self.columns_frame")
        self.columns_frame.bind("<Configure>", self.on_frame_configure)
        self.columns_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        ttk.Button(bottom_frame, text="Generate Report", command=self.show_chart_selection_dialog).pack()
        ttk.Button(bottom_frame, text="Generate Interactive Map", command=self.generate_map).pack()
        ttk.Label(top_frame, text=f"Version: {APP_VERSION}").pack(side='left', padx=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls *.xlsm")])
        if file_path:
            self.df, self.columns = load_data(file_path)
            if self.df is not None:
                for widget in self.columns_frame.winfo_children():
                    widget.destroy()
                self.column_vars = {}
                for column in self.columns:
                    var = IntVar()
                    chk = ttk.Checkbutton(self.columns_frame, text=column, variable=var)
                    chk.pack(anchor='w')
                    self.column_vars[column] = var

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = folder_selected
            logging.info(f"Output folder selected: {self.output_folder}")

    def show_chart_selection_dialog(self):
        selected_columns = [column for column, var in self.column_vars.items() if var.get() == 1]
        if not selected_columns:
            messagebox.showerror("Error", "No columns selected.")
            return
        ChartSelectionDialog(self.root, selected_columns, self.set_column_chart_pairs)

    def set_column_chart_pairs(self, column_chart_pairs):
        self.column_chart_pairs = column_chart_pairs
        self.generate_report()

    def generate_report(self):
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder first.")
            return
        if not self.column_chart_pairs:
            messagebox.showerror("Error", "No columns selected.")
            return
        if not self.config:
            messagebox.showerror("Error", "Configuration not loaded.")
            return
        charts = generate_charts(self.df, self.column_chart_pairs, self.config, self.output_folder)
        create_pdf_report(self.config, charts, self.output_folder)

    def generate_map(self):
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder first.")
            return
        lat_col = self.get_selected_coordinate_column("Latitude Column (Y)")
        lon_col = self.get_selected_coordinate_column("Longitude Column (X)")
        if lat_col and lon_col:
            generate_interactive_map(self.df, lat_col, lon_col, self.output_folder)

    def get_selected_coordinate_column(self, prompt):
        columns = [column for column, var in self.column_vars.items() if var.get() == 1]
        if not columns:
            messagebox.showerror("Error", f"No columns selected for {prompt}.")
            return None
        selection = simpledialog.askstring("Select Column", f"Select {prompt}:", initialvalue=columns[0])
        if selection and selection in columns:
            return selection
        else:
            messagebox.showerror("Error", f"Invalid selection for {prompt}.")
            return None

    def on_frame_configure(self, event):
        self.columns_canvas.configure(scrollregion=self.columns_canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        if self.root.tk.call('tk', 'windowingsystem') == 'win32':
            self.columns_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.columns_canvas.yview_scroll(int(-1 * event.delta), "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
