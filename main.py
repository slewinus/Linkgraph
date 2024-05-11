import tkinter as tk
from tkinter import filedialog, messagebox, IntVar, Scrollbar, Canvas, simpledialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
import folium
from PIL import Image, ImageTk
from PIL.Image import Resampling
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import json
import os
import sys
import logging

APP_VERSION = "BETA V0.1.9"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    try:
        config_path = os.path.join(sys._MEIPASS, "config.json") if getattr(sys, 'frozen', False) else "config.json"
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        logging.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        messagebox.showerror("Error", f"Failed to load config file: {str(e)}")
        return None

def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        logging.info(f"Excel file {file_path} loaded successfully.")
        return df, df.columns.tolist()
    except Exception as e:
        logging.error(f"Error loading Excel file: {e}")
        messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        return None, []

def is_numeric_column(series):
    return pd.api.types.is_numeric_dtype(series)

def generate_charts(df, column_chart_pairs, config, output_folder):
    figsize = (8, 6)
    for column, chart_type in column_chart_pairs:
        if column in df.columns:
            value_counts = df[column].value_counts()
            plt.figure(figsize=figsize)
            if chart_type == 'Pie Chart':
                if not value_counts.empty and value_counts.sum() > 0:
                    plt.pie(value_counts, autopct='%1.1f%%', startangle=90, colors=config['data_colors'][:len(value_counts)])
                    plt.legend(value_counts.index, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                    plt.axis('equal')
                else:
                    logging.info(f"No data to plot for {column} (Pie Chart).")
                    continue
            elif chart_type == 'Bar Chart':
                value_counts.plot(kind='bar', color=config['data_colors'])
                plt.ylabel('Count')
                plt.xlabel(column)
                plt.xticks(rotation=45)
            elif chart_type == 'Line Chart':
                if is_numeric_column(df[column]):
                    df[column].plot(kind='line', color=config['data_colors'][0])
                    plt.ylabel(column)
                    plt.xlabel('Index')
                else:
                    logging.warning(f"{column} contains non-numeric data. Skipping Line Chart.")
                    continue
            elif chart_type == 'Scatter Plot':
                other_columns = [col for col, _ in column_chart_pairs if col != column and is_numeric_column(df[col])]
                if other_columns:
                    plt.scatter(df[other_columns[0]], df[column], color=config['data_colors'][0])
                    plt.xlabel(other_columns[0])
                    plt.ylabel(column)
                else:
                    logging.warning(f"Scatter Plot requires at least two numeric columns. Skipping Scatter Plot for {column}.")
                    continue
            img_file_path = os.path.join(output_folder, f'{column.replace(" - ", "_").replace(" ", "_")}.png')
            plt.savefig(img_file_path, bbox_inches='tight')
            plt.close()
            logging.info(f"{chart_type} generated for column {column}: {img_file_path}")
            yield column, img_file_path
        else:
            logging.warning(f"Column {column} not found in the DataFrame.")

def create_pdf_report(config, charts, output_folder):
    pdf_file_path = os.path.join(output_folder, f'Rapport_Analyse_{datetime.now().strftime("%Y_%m_%d")}.pdf')
    c = pdf_canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter
    for header, img_file_path in charts:
        img_width, img_height = 8 * inch, 6 * inch
        title_y_position = height - 1.5 * inch
        image_x = (width - img_width) / 2
        image_y = (height - img_height) / 2
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(config['color_title'])
        c.drawCentredString(width / 2, title_y_position, header)
        c.drawImage(img_file_path, image_x, image_y, width=img_width, height=img_height, preserveAspectRatio=True)
        logo_path = os.path.join(sys._MEIPASS, "images", "logo.png") if getattr(sys, 'frozen', False) else "images/logo.png"
        c.drawImage(logo_path, inch * 0.5, inch * 0.5, width=1 * inch, height=0.5 * inch, preserveAspectRatio=True)
        c.setFont("Helvetica", 9)
        c.setFillColor(config['color_text'])
        c.drawString(2 * inch, inch * 0.25, f"Date de création : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.showPage()
    c.save()
    logging.info(f"PDF report generated: {pdf_file_path}")
    messagebox.showinfo("Success", f"PDF file has been generated successfully: {pdf_file_path}")

def generate_interactive_map(df, lat_col, lon_col, output_folder):
    if lat_col not in df.columns or lon_col not in df.columns:
        messagebox.showerror("Error", "Invalid latitude or longitude column selection.")
        return
    df = df[[lat_col, lon_col]].dropna()
    if df.empty:
        messagebox.showerror("Error", "No valid coordinates found after removing missing values.")
        return
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=f"{lat_col}: {row[lat_col]}, {lon_col}: {row[lon_col]}"
        ).add_to(m)
    map_file_path = os.path.join(output_folder, f'Interactive_Map_{datetime.now().strftime("%Y_%m_%d")}.html')
    m.save(map_file_path)
    logging.info(f"Interactive map generated: {map_file_path}")
    messagebox.showinfo("Success", f"Interactive map has been generated successfully: {map_file_path}")

class ChartSelectionDialog(tk.Toplevel):
    def __init__(self, parent, columns, callback):
        super().__init__(parent)
        self.title("Select Chart Types")
        self.geometry("400x400")
        self.chart_type_vars = {}
        self.callback = callback
        chart_types = ['Pie Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        frame = tk.Frame(self)
        frame.pack(pady=10, padx=10, fill='both', expand=True)
        for column in columns:
            var = tk.StringVar(value='Pie Chart')
            row_frame = tk.Frame(frame)
            row_frame.pack(anchor='w', fill='x')
            tk.Label(row_frame, text=column).pack(side='left', padx=10)
            chart_type_menu = ttk.Combobox(row_frame, textvariable=var, values=chart_types, state='readonly')
            chart_type_menu.pack(side='left')
            self.chart_type_vars[column] = var
        tk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

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
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, padx=10, fill='x')
        middle_frame = tk.Frame(root)
        middle_frame.pack(pady=10, padx=10, fill='both', expand=True)
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10, padx=10, fill='x')
        logo_path = os.path.join(sys._MEIPASS, "images", "icon_app.png") if getattr(sys, 'frozen', False) else "images/icon_app.png"
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((50, 50), Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_frame, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side='left')
        tk.Button(top_frame, text="Open Excel File", command=self.open_file).pack(side='left', padx=10)
        tk.Button(top_frame, text="Select Output Folder", command=self.select_output_folder).pack(side='left', padx=10)
        self.columns_canvas = tk.Canvas(middle_frame)
        self.columns_frame = tk.Frame(self.columns_canvas)
        self.vsb = Scrollbar(middle_frame, orient="vertical", command=self.columns_canvas.yview)
        self.columns_canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_canvas.create_window((4, 4), window=self.columns_frame, anchor="nw", tags="self.columns_frame")
        self.columns_frame.bind("<Configure>", self.on_frame_configure)
        self.columns_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        tk.Button(bottom_frame, text="Generate Report", command=self.show_chart_selection_dialog).pack()
        tk.Button(bottom_frame, text="Generate Interactive Map", command=self.generate_map).pack()
        tk.Label(top_frame, text=f"Version: {APP_VERSION}").pack(side='left', padx=10)

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
                    chk = tk.Checkbutton(self.columns_frame, text=column, variable=var)
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
