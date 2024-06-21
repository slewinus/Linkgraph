
# Linkgraph

Linkgraph is a tool designed to analyze and visualize data from Excel files. It allows users to select specific columns and chart types (Pie, Histogram, Line, Scatter) to generate visual reports & interactive maps. Users can save these visualizations as images and create comprehensive PDF reports that include charts, titles, dates, logos, and configuration details. The tool supports interactive selection of Excel sheets and output folders, making it easy to organize and present data effectively.

# Installation

To install and set up Linkgraph, follow these steps:

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/slewinus/Linkgraph.git
   cd Linkgraph
   ```

2. **Create a Virtual Environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```sh
   python main.py
   ```

    # Documentation

## Usage

### Launch the Application
1. Double-click the application icon to launch it.
2. Follow any initial setup prompts.

### Load an Excel File
1. Click the "Open Excel File" button.
2. Select and open the desired Excel file.

### Select Columns for Analysis
1. Choose the columns you want to include in the analysis using the checkboxes.

### Choose an Output Folder
1. Click the "Select Output Folder" button.
2. Select the folder where reports and charts will be saved.

### Generate Charts
1. Click the "Generate Report" button.
2. Select the desired chart types (Pie, Histogram, Line, Scatter) for each column.
3. Confirm your choices to generate and save the charts.

### Generate an Interactive Map
1. Click the "Generate Interactive Map" button.
2. The application will automatically detect columns with GPS coordinates and include them in the map.

### Verify Generated Files
1. Check the output folder for:
   - PDF reports with generated charts.
   - PNG images of the charts.
   - HTML files for the interactive maps.

### Close the Application
1. Click the close button (X) in the upper right corner of the window.

### Notes
- Ensure latitude and longitude columns are correctly named for automatic detection.
- Available chart types depend on the nature of the data (numeric data required for line and scatter plots).

## Running Tests

To ensure Linkgraph is functioning correctly, you can run the provided tests. Follow these steps to execute the tests:

1. **Navigate to the Project Directory:**
   ```sh
   cd Linkgraph
   ```

2. **Activate the Virtual Environment:**
   ```sh
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Run the Tests:**
   ```sh
   python -m unittest discover -s test
   ```

This command will automatically discover and execute all test cases within the `test` directory. Ensure you have the necessary test files in this directory.


## License

[MIT](https://choosealicense.com/licenses/mit/)

