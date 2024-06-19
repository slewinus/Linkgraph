import logging
import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox, IntVar
from PIL import Image
from PIL.Image import Resampling
import re

from config import apply_style, load_config
from interactive_map import generate_interactive_map
from reports import load_data, generate_charts, create_pdf_report

APP_VERSION = "BETA V0.2.0"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set appearance mode and default theme
ctk.set_appearance_mode("Light")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

def detect_gps_columns(df):
    lat_col = None
    lon_col = None
    for col in df.columns:
        if re.search(r'latitude|lat|gps y', col, re.IGNORECASE):
            lat_col = col
        if re.search(r'longitude|lon|gps x', col, re.IGNORECASE):
            lon_col = col
    return lat_col, lon_col

class ChartSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, columns, callback):
        super().__init__(parent)
        self.title("Select Chart Types")
        self.geometry("400x400")
        self.chart_type_vars = {}
        self.display_type_vars = {}
        self.callback = callback
        chart_types = ['Pie Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        display_types = ['%', 'Nombre']
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=10, fill='both', expand=True)
        for column in columns:
            var = ctk.StringVar(value='Pie Chart')
            display_var = ctk.StringVar(value='%')
            row_frame = ctk.CTkFrame(frame)
            row_frame.pack(anchor='w', fill='x')
            ctk.CTkLabel(row_frame, text=column).pack(side='left', padx=10)
            chart_type_menu = ctk.CTkOptionMenu(row_frame, variable=var, values=chart_types)
            chart_type_menu.pack(side='left')
            display_type_menu = ctk.CTkOptionMenu(row_frame, variable=display_var, values=display_types)
            display_type_menu.pack(side='left')
            self.chart_type_vars[column] = var
            self.display_type_vars[column] = display_var
        ctk.CTkButton(self, text="OK", command=self.on_ok).pack(pady=10)

    def on_ok(self):
        column_chart_pairs = [(column, var.get(), self.display_type_vars[column].get()) for column, var in self.chart_type_vars.items()]
        self.callback(column_chart_pairs)
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.df = None
        self.columns = []
        self.column_vars = {}
        self.output_folder = ""
        self.config = load_config()

        # Configure window
        self.title('Linkgraph')
        self.geometry("750x600")
        apply_style(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        self.middle_frame = ctk.CTkFrame(self, corner_radius=0)
        self.middle_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=0)
        self.bottom_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

        # Correctly handle file paths for PyInstaller
        logo_path = os.path.join(sys._MEIPASS, "images", "icon_app.png") if getattr(sys, 'frozen', False) else "images/icon_app.png"
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((50, 50), Resampling.LANCZOS)

        # Create CTkImage object
        logo_ctk_image = ctk.CTkImage(light_image=logo_image, size=(50, 50))

        logo_label = ctk.CTkLabel(self.top_frame, image=logo_ctk_image, text="")
        logo_label.grid(row=0, column=0, padx=10)

        ctk.CTkButton(self.top_frame, text="Ouvrir le fichier Excel", command=self.open_file).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.top_frame, text="Choisir le dossier de sortie", command=self.select_output_folder).grid(row=0, column=2, padx=10)

        # Add dropdown menu for changing appearance mode
        appearance_mode_var = ctk.StringVar(value="System")
        appearance_menu = ctk.CTkOptionMenu(self.top_frame, variable=appearance_mode_var, values=["Light", "Dark"], command=self.change_appearance_mode)
        appearance_menu.grid(row=0, column=3, padx=10)

        self.columns_canvas = ctk.CTkCanvas(self.middle_frame)
        self.columns_frame = ctk.CTkFrame(self.columns_canvas)
        self.vsb = ctk.CTkScrollbar(self.middle_frame, command=self.columns_canvas.yview)
        self.columns_canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_canvas.create_window((4, 4), window=self.columns_frame, anchor="nw", tags="self.columns_frame")
        self.columns_frame.bind("<Configure>", self.on_frame_configure)

        buttons_frame = ctk.CTkFrame(self.bottom_frame)
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="Generer le rappport", command=self.show_chart_selection_dialog, fg_color="#0078D4", text_color="#FFF6E9").pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Generer la carte interactive", command=self.generate_map, fg_color="#0078D4", text_color="#FFF6E9").pack(side='left', padx=5)

        ctk.CTkLabel(self.top_frame, text=f"Version: {APP_VERSION}").grid(row=0, column=4, padx=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Choisir le Fichier Excel", filetypes=[("Excel files", "*.xlsx *.xls *.xlsm")])
        if file_path:
            self.df, self.columns = load_data(file_path)
            if self.df is not None:
                for widget in self.columns_frame.winfo_children():
                    widget.destroy()
                self.column_vars = {}
                for column in self.columns:
                    var = IntVar()
                    chk = ctk.CTkCheckBox(self.columns_frame, text=column, variable=var, fg_color="#0078D4", text_color="#FFF6E9")
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
            messagebox.showerror("Erreur", "Aucune colonne sélectionnée.")
            return
        ChartSelectionDialog(self, selected_columns, self.set_column_chart_pairs)

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
        messagebox.showinfo("Success", "PDF file has been generated successfully.")

    def generate_map(self):
        lat_col, lon_col = detect_gps_columns(self.df)
        if lat_col and lon_col:
            additional_columns = [column for column, var in self.column_vars.items() if var.get() == 1 and column not in [lat_col, lon_col]]
            generate_interactive_map(self.df, lat_col, lon_col, additional_columns, self.output_folder)
        else:
            messagebox.showerror("Error", "latitude ou longitude non trouvée.")

    def on_frame_configure(self, event):
        self.columns_canvas.configure(scrollregion=self.columns_canvas.bbox("all"))

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        self.update_background_colors()

    def update_background_colors(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            bg_color = "#333333"
            fg_button_color = "#000000"
        elif current_mode == "Light":
            bg_color = "#F6F5F2"
            fg_button_color = "#F6F5F2"
        else:  # system
            bg_color = "#F0F0F0"
            fg_button_color = "#0078D4"

        self.configure(bg=bg_color)
        self.top_frame.configure(fg_color=bg_color)
        self.middle_frame.configure(fg_color=bg_color)
        self.bottom_frame.configure(fg_color=bg_color)
        self.columns_canvas.configure(bg=bg_color)
        self.columns_frame.configure(fg_color=bg_color)

        # Update button colors
        for button in self.bottom_frame.winfo_children():
            if isinstance(button, ctk.CTkButton):
                button.configure(fg_color=fg_button_color, text_color=bg_color)

if __name__ == "__main__":
    app = App()
    app.mainloop()
