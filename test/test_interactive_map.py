import unittest
from unittest.mock import patch
import pandas as pd
from interactive_map import generate_interactive_map

class TestGenerateInteractiveMap(unittest.TestCase):
    @patch('interactive_map.messagebox.showerror')
    def test_generate_interactive_map_invalid_columns(self, mock_showerror):
        df = pd.DataFrame({
            'lat': [1, 2],
            'lon': [3, 4],
            'other': [5, 6]
        })
        generate_interactive_map(df, 'invalid_lat', 'invalid_lon', ['other'], 'output_folder')
        mock_showerror.assert_called_with("Error", "Invalid latitude or longitude column selection.")

    @patch('interactive_map.folium.Map.save')
    @patch('interactive_map.folium.plugins.MarkerCluster.add_to')
    @patch('interactive_map.folium.Map')
    def test_generate_interactive_map_success(self, mock_map, mock_marker_cluster_add_to, mock_save):
        df = pd.DataFrame({
            'lat': [1, 2],
            'lon': [3, 4],
            'FTTO': ['éligible', 'Non éligible'],
            'FTTH': ['éligible', 'Non éligible']
        })
        mock_map_instance = mock_map.return_value
        generate_interactive_map(df, 'lat', 'lon', ['FTTO', 'FTTH'], 'output_folder')

        mock_map.assert_called_with(location=[1.5, 3.5], zoom_start=6)
        mock_marker_cluster_add_to.assert_called()
        mock_map_instance.save.assert_called()

if __name__ == '__main__':
    unittest.main()
