import logging
import os
import re
import folium
import folium.plugins as plugins
from datetime import datetime
from tkinter import messagebox


def detect_gps_columns(df):
    lat_col = None
    lon_col = None
    for col in df.columns:
        if re.search(r'latitude|lat|gps y', col, re.IGNORECASE):
            lat_col = col
        if re.search(r'longitude|lon|gps x', col, re.IGNORECASE):
            lon_col = col
    return lat_col, lon_col


def generate_interactive_map(df, lat_col, lon_col, additional_columns, output_folder):
    if lat_col not in df.columns or lon_col not in df.columns:
        messagebox.showerror("Error", "Invalid latitude or longitude column selection.")
        return
    df = df[[lat_col, lon_col] + additional_columns].dropna()
    if df.empty:
        messagebox.showerror("Error", "No valid coordinates found after removing missing values.")
        return

    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
    marker_cluster = plugins.MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_text = ""
        for col in additional_columns:
            popup_text += f"{col}: {row[col]}<br>"

        color = "green"

        for col in additional_columns:
            if "non éligible" in str(row[col]).lower():
                color = "red"
                break

        if 'FTTO' in df.columns:
            if "éligible" in str(row['FTTO']).lower():
                color = "orange"
            elif "Non éligible" in str(row['FTTO']).lower():
                color = "purple"
            elif "Sur Devis - 1G" in str(row['FTTO']).lower():
                color = "orange"
        if 'FTTH' in df.columns:
            if "éligible" in str(row['FTTH']).lower():
                color = "blue"
            elif "Non éligible" in str(row['FTTH']).lower():
                color = "black"

        marker = folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=popup_text.strip("<br>"),
            icon=folium.Icon(color=color)
        )
        marker.add_to(marker_cluster)

    map_file_path = os.path.join(output_folder, f'Interactive_Map_{datetime.now().strftime("%Y_%m_%d")}.html')
    m.save(map_file_path)

    logging.info(f"Interactive map generated: {map_file_path}")
    messagebox.showinfo("Success", f"Interactive map has been generated successfully: {map_file_path}")
