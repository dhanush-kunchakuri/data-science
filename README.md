# Titanic Data Cleaning and Analysis Web Application

A user-friendly web application that allows you to upload CSV files, clean the data, and perform basic analysis with visualizations.

## Features

- **File Upload**: Easily upload your CSV files
- **Data Preview**: View the first 10 rows of your dataset
- **Data Cleaning**:
  - Handle missing values (drop or fill with mean/median/mode)
  - Automatic detection of data types
  - Summary statistics for numeric and categorical columns
- **Visualizations**:
  - Distribution plots for numeric columns
  - Correlation heatmap
- **Export**: Download the cleaned dataset as a CSV file

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data_science_project
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Open your web browser** and go to:
   ```
   http://127.0.0.1:5000/
   ```

3. **Upload a CSV file** using the upload interface

4. **Clean and analyze** your data using the interactive interface

## Project Structure

```
data_science_project/
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/              # Static files (CSS, JS, images)
│   └── plots/           # Generated visualization images
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home/upload page
│   └── analysis.html    # Data analysis page
└── uploads/             # Temporary storage for uploaded files
```

## Technologies Used

- **Backend**:
  - Python 3.8+
  - Flask (Web Framework)
  - Pandas (Data Manipulation)
  - NumPy (Numerical Operations)
  - Matplotlib & Seaborn (Visualization)

- **Frontend**:
  - HTML5
  - CSS3 (with Bootstrap 5)
  - JavaScript (for interactivity)

## License

This project is open source and available under the [MIT License](LICENSE).
