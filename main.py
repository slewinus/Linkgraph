import logging
import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, IntVar
from PIL import ImageTk, Image
from PIL.Image import Resampling

from config import apply_style, load_config
from interactive_map import generate_interactive_map
from reports import load_data, generate_charts, create_pdf_report

APP_VERSION = "BETA V0.1.9"
logging.basicConfig(level=logging.INFO, format='%(pastime)s - %(levelness)s - %(message)s')


class ChartSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, columns, callback):

        super().__init__(parent)
        self.title("Select Chart Types")
        self.geometry("400x400")
        self.chart_type_vars = {}
        self.callback = callback
        chart_types = ['Pie Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=10, fill='both', expand=True)
        for column in columns:
            var = ctk.StringVar(value='Pie Chart')
            row_frame = ctk.CTkFrame(frame)
            row_frame.pack(anchor='w', fill='x')
            ctk.CTkLabel(row_frame, text=column).pack(side='left', padx=10)
            chart_type_menu = ctk.CTkOptionMenu(row_frame, variable=var, values=chart_types)
            chart_type_menu.pack(side='left')
            self.chart_type_vars[column] = var
        ctk.CTkButton(self, text="OK", command=self.on_ok).pack(pady=10)

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
        root.title('Report Generator')
        root.geometry("750x600")
        apply_style(root)  # Apply the custom style if needed

        top_frame = ctk.CTkFrame(root)
        top_frame.pack(pady=10, padx=10, fill='x')
        middle_frame = ctk.CTkFrame(root)
        middle_frame.pack(pady=10, padx=10, fill='both', expand=True)
        bottom_frame = ctk.CTkFrame(root)
        bottom_frame.pack(pady=10, padx=10, fill='x')

        logo_path = os.path.join(sys._MEIPASS, "images", "icon_app.png") if getattr(sys, 'frozen',
                                                                                    False) else "images/icon_app.png"
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((50, 50), Resampling.LANCZOS)
        logo_photo = ctk.CTkImage(logo_image)
        logo_label = ctk.CTkLabel(top_frame, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side='left')

        ctk.CTkButton(top_frame, text="Open Excel File", command=self.open_file).pack(side='left', padx=10)
        ctk.CTkButton(top_frame, text="Select Output Folder", command=self.select_output_folder).pack(side='left',
                                                                                                      padx=10)

        self.columns_canvas = ctk.CTkCanvas(middle_frame)
        self.columns_frame = ctk.CTkFrame(self.columns_canvas)
        self.vsb = ctk.CTkScrollbar(middle_frame, command=self.columns_canvas.yview)
        self.columns_canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_canvas.create_window((4, 4), window=self.columns_frame, anchor="nw", tags="self.columns_frame")
        self.columns_frame.bind("<Configure>", self.on_frame_configure)

        ctk.CTkButton(bottom_frame, text="Generate Report", command=self.show_chart_selection_dialog).pack()
        ctk.CTkButton(bottom_frame, text="Generate Interactive Map", command=self.generate_map).pack()
        ctk.CTkLabel(top_frame, text=f"Version: {APP_VERSION}").pack(side='left', padx=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel File",
                                               filetypes=[("Excel files", "*.xlsx *.xls *.xlsm")])
        if file_path:
            self.df, self.columns = load_data(file_path)
            if self.df is not None:
                for widget in self.columns_frame.winfo_children():
                    widget.destroy()
                self.column_vars = {}
                for column in self.columns:
                    var = IntVar()
                    chk = ctk.CTkCheckBox(self.columns_frame, text=column, variable=var)
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
        lat_col = self.get_selected_coordinate_column("Latitude Column (Y)")
        lon_col = self.get_selected_coordinate_column("Longitude Column (X)")
        if lat_col and lon_col:
            additional_columns = [column for column, var in self.column_vars.items() if var.get() == 1 and column not in [lat_col, lon_col]]
            generate_interactive_map(self.df, lat_col, lon_col, additional_columns, self.output_folder)

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


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
