#############################
#  By: Oscar Robert-Besle   #
#  Last update : 3 May 2024 #
#############################
import tkinter as tk
from tkinter import filedialog, messagebox, Checkbutton, IntVar, Scrollbar, Canvas
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from PIL.Image import Resampling
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime
import json
import os
import logging

APP_VERSION = "1.0.0"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        logging.info("Excel file loaded successfully.")
        return df, df.columns.tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        return None, []

def generate_pie_charts(df, selected_columns, config, output_folder):
    figsize = (10, 6)  # Adjusted for better visualization with side legends
    for header in selected_columns:
        if header in df.columns:
            value_counts = df[header].value_counts()
            if not value_counts.empty and value_counts.sum() > 0:
                plt.figure(figsize=figsize)
                patches, texts, autotexts = plt.pie(value_counts, startangle=90, colors=config['data_colors'][:len(value_counts)], autopct='%1.1f%%')
                plt.legend(patches, [f'{l}: {s}' for l, s in zip(value_counts.index, value_counts)], title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                plt.axis('equal')
                img_file_path = os.path.join(output_folder, f'{header.replace(" - ", "_").replace(" ", "_")}.png')
                plt.savefig(img_file_path, bbox_inches='tight')
                plt.close()
                yield header, img_file_path
            else:
                logging.info(f"No data to graph for {header}.")
        else:
            logging.warning(f"Column {header} not found in the file.")


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
        c.drawImage(config['logo_path'], inch * 0.5, inch * 0.5, width=1 * inch, height=0.5 * inch, preserveAspectRatio=True)
        c.setFont("Helvetica", 9)
        c.setFillColor(config['color_text'])
        c.drawString(2 * inch, inch * 0.25, f"Date de création : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.showPage()
    c.save()
    messagebox.showinfo("Success", f"PDF file has been generated successfully: {pdf_file_path}")

class App:
    def __init__(self, root):
        self.root = root
        self.df = None
        self.columns = []
        self.column_vars = []
        self.output_folder = ""

        root.title('Report Generator')
        config = load_config()

        # Layout using frames
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, padx=10, fill='x')
        middle_frame = tk.Frame(root)
        middle_frame.pack(pady=10, padx=10, fill='both', expand=True)
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10, padx=10, fill='x')

        # Logo
        logo_image = Image.open(config['logo_path'])
        logo_image = logo_image.resize((100, 50), Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_frame, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side='left')

        # File and Folder Buttons
        tk.Button(top_frame, text="Open Excel File", command=self.open_file).pack(side='left', padx=10)
        tk.Button(top_frame, text="Select Output Folder", command=self.select_output_folder).pack(side='left', padx=10)

        # Column Selection Area with Scrollbar
        self.columns_canvas = tk.Canvas(middle_frame)
        self.columns_frame = tk.Frame(self.columns_canvas)
        self.vsb = tk.Scrollbar(middle_frame, orient="vertical", command=self.columns_canvas.yview)
        self.columns_canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_canvas.create_window((4,4), window=self.columns_frame, anchor="nw", tags="self.columns_frame")

        self.columns_frame.bind("<Configure>", self.onFrameConfigure)
        self.columns_canvas.bind_all("<MouseWheel>", self.onMouseWheel)  # Bind mouse wheel event

        # Generate Report Button
        tk.Button(bottom_frame, text="Generate Report", command=self.generate).pack()
        version_label = tk.Label(top_frame, text=f"Version: {APP_VERSION}")
        version_label.pack(side='left', padx=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls *.xlsm")])
        if file_path:
            self.df, self.columns = load_data(file_path)
            if self.df is not None:
                for widget in self.columns_frame.winfo_children():
                    widget.destroy()
                self.column_vars = []
                for column in self.columns:
                    var = IntVar()
                    chk = Checkbutton(self.columns_frame, text=column, variable=var)
                    chk.pack(anchor='w')
                    self.column_vars.append((var, column))

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.columns_canvas.configure(scrollregion=self.columns_canvas.bbox("all"))

    def onMouseWheel(self, event):
        """Handle mouse wheel scroll for Windows and Unix systems."""
        if self.root.tk.call('tk', 'windowingsystem')=='win32':
            self.columns_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            self.columns_canvas.yview_scroll(int(-1*event.delta), "units")

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = folder_selected
            logging.info(f"Output folder selected: {self.output_folder}")

    def generate(self):
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder first.")
            return
        selected_columns = [var_column[1] for var_column in self.column_vars if var_column[0].get() == 1]
        if not selected_columns:
            messagebox.showerror("Error", "No columns selected.")
            return
        charts = generate_pie_charts(self.df, selected_columns, load_config(), self.output_folder)
        create_pdf_report(load_config(), charts, self.output_folder)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
