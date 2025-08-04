from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
from io import StringIO
import matplotlib
matplotlib.use('Agg')  # Required for non-interactive plotting
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

# Ensure upload and static directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'plots'), exist_ok=True)

# Global variable to store the current dataframe
df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                # Read the uploaded CSV file
                df = pd.read_csv(file)
                
                # Get basic info about the data
                data_info = {
                    'shape': df.shape,
                    'columns': df.columns.tolist(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'data_types': df.dtypes.astype(str).to_dict()
                }
                
                # Generate basic visualizations
                plot_paths = generate_visualizations(df)
                
                return render_template('analysis.html', 
                                    data_info=data_info, 
                                    plot_paths=plot_paths,
                                    sample_data=df.head(10).to_dict('records'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file')
            return redirect(request.url)
    
    return render_template('index.html')

def generate_visualizations(df):
    """Generate basic visualizations for the uploaded data"""
    plot_paths = {}
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 1. Numeric columns distribution
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        plt.figure(figsize=(10, 6))
        for i, col in enumerate(numeric_cols[:3]):  # Limit to first 3 numeric columns
            plt.subplot(1, min(3, len(numeric_cols)), i+1)
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f'Distribution of {col}')
            plt.xticks(rotation=45)
        plt.tight_layout()
        dist_plot_path = f"static/plots/distribution_{timestamp}.png"
        plt.savefig(dist_plot_path)
        plot_paths['distribution'] = dist_plot_path
        plt.close()
    
    # 2. Correlation heatmap (if enough numeric columns)
    if len(numeric_cols) > 2:
        plt.figure(figsize=(10, 8))
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Heatmap')
        corr_plot_path = f"static/plots/correlation_{timestamp}.png"
        plt.savefig(corr_plot_path)
        plot_paths['correlation'] = corr_plot_path
        plt.close()
    
    return plot_paths

@app.route('/clean', methods=['POST'])
def clean_data():
    global df
    
    if df is None:
        flash('No data to clean. Please upload a file first.')
        return redirect(url_for('index'))
    
    try:
        # Get cleaning options from the form
        drop_na_cols = request.form.getlist('drop_na_cols')
        fill_na_strategy = request.form.get('fill_na_strategy', 'mean')
        
        # Apply cleaning
        if drop_na_cols:
            if 'all' in drop_na_cols:
                df.dropna(inplace=True)
            else:
                df.dropna(subset=drop_na_cols, inplace=True)
        
        # Fill remaining NA values based on strategy
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            if df[col].isna().any():
                if fill_na_strategy == 'mean':
                    df[col].fillna(df[col].mean(), inplace=True)
                elif fill_na_strategy == 'median':
                    df[col].fillna(df[col].median(), inplace=True)
                elif fill_na_strategy == 'mode':
                    df[col].fillna(df[col].mode()[0], inplace=True)
        
        # For categorical columns, fill with mode
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].isna().any():
                df[col].fillna(df[col].mode()[0], inplace=True)
        
        flash('Data cleaned successfully!', 'success')
        
        # Get updated data info
        data_info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Generate new visualizations
        plot_paths = generate_visualizations(df)
        
        return render_template('analysis.html', 
                            data_info=data_info, 
                            plot_paths=plot_paths,
                            sample_data=df.head(10).to_dict('records'))
    
    except Exception as e:
        flash(f'Error cleaning data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download')
def download_data():
    global df
    if df is not None:
        # Create a StringIO buffer
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name='cleaned_data.csv'
        )
    else:
        flash('No data to download. Please upload and process a file first.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
