from datetime import datetime
from tkinter import messagebox
import folium
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

    # Create a map and save it
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
    marker_cluster = folium.FeatureGroup(name="Markers").add_to(m)

    markers = []
    for _, row in df.iterrows():
        popup_text = f"GPS Y: {row[lat_col]}, GPS X: {row[lon_col]}"
        for col in additional_columns:
            popup_text += f"<br>{col}: {row[col]}"

        color = "blue"  # Default color
        if 'FTTH' in additional_columns:
            color = "green" if row['FTTH'] == "Eligible" else "red"

        marker = folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=popup_text,
            icon=folium.Icon(color=color)
        )
        marker.add_to(marker_cluster)
        markers.append(marker)

    map_file_path = os.path.join(output_folder, f'Interactive_Map_{datetime.now().strftime("%Y_%m_%d")}.html')
    m.save(map_file_path)

    # Read the HTML file and inject filter controls and JavaScript
    with open(map_file_path, 'r') as f:
        html_content = f.read()

    filter_controls = """
    <div style="position: fixed; top: 10px; left: 10px; background: white; padding: 10px; z-index: 1000;">
        <label for="ftthFilter">FTTH:</label>
        <select id="ftthFilter" onchange="filterMarkers()">
            <option value="All">All</option>
            <option value="Eligible">Eligible</option>
            <option value="Non éligible">Non éligible</option>
        </select>
        <label for="fttoFilter">FTTO:</label>
        <select id="fttoFilter" onchange="filterMarkers()">
            <option value="All">All</option>
            <option value="Eligible">Eligible</option>
            <option value="Non éligible">Non éligible</option>
        </select>
        <label for="operatorFilter">Operator:</label>
        <select id="operatorFilter" onchange="filterMarkers()">
            <option value="All">All</option>
            <option value="Orange">Orange</option>
            <option value="SFR">SFR</option>
            <option value="Bouygues">Bouygues</option>
            <option value="Free">Free</option>
        </select>
    </div>
    """

    filter_script = """
    <script>
    var map = L.map('map').setView([0, 0], 1); // Initialize the map correctly
    var markers = []; // Initialize markers array
    function filterMarkers() {
        var ftthFilter = document.getElementById('ftthFilter').value;
        var fttoFilter = document.getElementById('fttoFilter').value;
        var operatorFilter = document.getElementById('operatorFilter').value;

        for (var i = 0; i < markers.length; i++) {
            var marker = markers[i];
            var popupContent = marker.getPopup().getContent();
            var showMarker = true;

            if (ftthFilter !== 'All' && popupContent.indexOf('FTTH: ' + ftthFilter) === -1) {
                showMarker = false;
            }

            if (fttoFilter !== 'All' && popupContent.indexOf('FTTO: ' + fttoFilter) === -1) {
                showMarker = false;
            }

            if (operatorFilter !== 'All' && popupContent.indexOf(operatorFilter) === -1) {
                showMarker = false;
            }

            if (showMarker) {
                marker.addTo(map);
            } else {
                map.removeLayer(marker);
            }
        }
    }
    </script>
    <script>
    """

    # Add marker initialization script
    for _, row in df.iterrows():
        lat, lon = row[lat_col], row[lon_col]
        popup_content = f"GPS Y: {row[lat_col]}, GPS X: {row[lon_col]}"
        for col in additional_columns:
            popup_content += f"<br>{col}: {row[col]}"
        color = "blue"  # Default color
        if 'FTTH' in additional_columns:
            color = "green" if row['FTTH'] == "Eligible" else "red"
        marker_script = f"""
        var marker = L.marker([{lat}, {lon}], {{icon: L.icon({{iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png', iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]}})}}).bindPopup("{popup_content}");
        markers.push(marker);
        marker.addTo(map);
        """
        filter_script += marker_script

    filter_script += "filterMarkers();</script>"

    # Insert the filter controls, map container and script into the HTML
    html_content = html_content.replace("<body>", f"<body>{filter_controls}<div id='map' style='width: 100%; height: 600px;'></div>")
    html_content = html_content.replace("</body>", f"{filter_script}</body>")

    with open(map_file_path, 'w') as f:
        f.write(html_content)

    logging.info(f"Interactive map generated: {map_file_path}")
    messagebox.showinfo("Success", f"Interactive map has been generated successfully: {map_file_path}")