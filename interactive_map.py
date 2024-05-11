from datetime import datetime
from tkinter import messagebox
import folium
import logging
import os



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