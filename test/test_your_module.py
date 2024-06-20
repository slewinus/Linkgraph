import unittest
import pandas as pd
from main import detect_gps_columns

class TestDetectGPSColumns(unittest.TestCase):
    def test_detect_gps_columns(self):
        df = pd.DataFrame({
            'Latitude': [1, 2, 3],
            'Longitude': [4, 5, 6],
            'Other': [7, 8, 9]
        })
        lat_col, lon_col = detect_gps_columns(df)
        self.assertEqual(lat_col, 'Latitude')
        self.assertEqual(lon_col, 'Longitude')

if __name__ == '__main__':
    unittest.main()
