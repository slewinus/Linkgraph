# reports.py
import logging
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas

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
    for column, chart_type, display_type in column_chart_pairs:
        if column in df.columns:
            value_counts = df[column].value_counts()
            plt.figure(figsize=figsize)
            if chart_type == 'Pie Chart':
                if not value_counts.empty and value_counts.sum() > 0:
                    if display_type == '%':
                        plt.pie(value_counts, autopct='%1.1f%%', startangle=90, colors=config['data_colors'][:len(value_counts)])
                    else:
                        plt.pie(value_counts, autopct=lambda p: f'{int(p * sum(value_counts) / 100)}', startangle=90, colors=config['data_colors'][:len(value_counts)])
                    plt.legend(value_counts.index, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                    plt.axis('equal')
            elif chart_type == 'Bar Chart':
                value_counts.plot(kind='bar', color=config['data_colors'])
                plt.ylabel('Count' if display_type == 'Nombre' else 'Percentage')
                plt.xlabel(column)
                plt.xticks(rotation=45)
                if display_type == '%':
                    total = value_counts.sum()
                    for i, value in enumerate(value_counts):
                        plt.text(i, value + 1, f'{(value / total) * 100:.1f}%', ha='center')
            elif chart_type == 'Line Chart':
                if is_numeric_column(df[column]):
                    df[column].plot(kind='line', color=config['data_colors'][0])
                    plt.ylabel(column)
                    plt.xlabel('Index')
            elif chart_type == 'Scatter Plot':
                other_columns = [col for col, _, _ in column_chart_pairs if col != column and is_numeric_column(df[col])]
                if other_columns:
                    plt.scatter(df[other_columns[0]], df[column], color=config['data_colors'][0])
                    plt.xlabel(other_columns[0])
                    plt.ylabel(column)
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
