from datetime import datetime
from tkinter import messagebox
import folium
import folium.plugins as plugins
import logging
import os

def generate_interactive_map(df, lat_col, lon_col, additional_columns, output_folder):
    if lat_col not in df.columns or lon_col not in df.columns:
        messagebox.showerror("Error", "Invalid latitude or longitude column selection.")
        return
    df = df[[lat_col, lon_col] + additional_columns].dropna()
    if df.empty:
        messagebox.showerror("Error", "No valid coordinates found after removing missing values.")
        return

    # Create a map
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
    marker_cluster = plugins.MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_text = f"GPS Y: {row[lat_col]}, GPS X: {row[lon_col]}"
        for col in additional_columns:
            popup_text += f"<br>{col}: {row[col]}"

        # Set default color to green
        color = "green"

        # Check if any additional column has "Non éligible"
        for col in additional_columns:
            if "non éligible" in str(row[col]).lower():
                color = "red"
                break  # Stop checking further if one "Non éligible" is found

        # Additional checks for FTTH and FTTO
        if 'FTTO' in df.columns:
            if "éligible" in str(row['FTTO']).lower():
                color = "orange"
            elif "non éligible" in str(row['FTTO']).lower():
                color = "purple"
        if 'FTTH' in df.columns:
            if "éligible" in str(row['FTTH']).lower():
                color = "blue"
            elif "non éligible" in str(row['FTTH']).lower():
                color = "black"

        marker = folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=popup_text,
            icon=folium.Icon(color=color)
        )
        marker.add_to(marker_cluster)

    map_file_path = os.path.join(output_folder, f'Interactive_Map_{datetime.now().strftime("%Y_%m_%d")}.html')
    m.save(map_file_path)

    logging.info(f"Interactive map generated: {map_file_path}")
    messagebox.showinfo("Success", f"Interactive map has been generated successfully: {map_file_path}")
