import unittest
from unittest.mock import patch
import pandas as pd
from reports import load_data

class TestLoadData(unittest.TestCase):
    @patch('pandas.read_excel')
    def test_load_data_success(self, mock_read_excel):
        mock_df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        mock_read_excel.return_value = mock_df
        df, columns = load_data('fake_path.xlsx')
        self.assertEqual(df.shape, (2, 2))
        self.assertListEqual(columns, ['col1', 'col2'])

    @patch('pandas.read_excel')
    def test_load_data_failure(self, mock_read_excel):
        mock_read_excel.side_effect = Exception('Error loading file')
        df, columns = load_data('fake_path.xlsx')
        self.assertIsNone(df)
        self.assertListEqual(columns, [])

if __name__ == '__main__':
    unittest.main()
