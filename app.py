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
                data_info = get_data_info(df)
                data_profile = get_data_profile(df)
                
                # Generate basic visualizations
                plot_paths = generate_visualizations(df)
                
                return render_template('analysis.html', 
                                    data_info=data_info, 
                                    data_profile=data_profile,
                                    data_summary=get_data_summary(df),
                                    plot_paths=plot_paths,
                                    sample_data=df.head(10).to_dict('records'),
                                    active_page='analysis')
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file')
            return redirect(request.url)
    
    return render_template('index.html', active_page='home')

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
    
    
    if len(numeric_cols) > 2:
        plt.figure(figsize=(10, 8))
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Heatmap')
        corr_plot_path = f"static/plots/correlation_{timestamp}.png"
        plt.savefig(corr_plot_path)
        plot_paths['correlation'] = corr_plot_path
        plt.close()
    
    # 3. Categorical top-value bar chart
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        for i, col in enumerate(categorical_cols[:2]):
            plt.figure(figsize=(8, 5))
            top_counts = df[col].value_counts().nlargest(6)
            sns.barplot(x=top_counts.values, y=top_counts.index, palette='crest')
            plt.title(f'Top Categories in {col}')
            plt.xlabel('Count')
            plt.ylabel(col)
            plt.tight_layout()
            cat_plot_path = f"static/plots/category_{col}_{timestamp}.png"
            plt.savefig(cat_plot_path)
            plot_paths[f'category_{col}'] = cat_plot_path
            plt.close()

    return plot_paths


def get_data_info(dataframe):
    return {
        'shape': dataframe.shape,
        'columns': dataframe.columns.tolist(),
        'missing_values': dataframe.isnull().sum().to_dict(),
        'data_types': dataframe.dtypes.astype(str).to_dict()
    }


def get_data_profile(dataframe):
    profile = []
    for col in dataframe.columns:
        values = dataframe[col]
        top_value = ''
        top_count = 0
        if not values.mode().empty:
            top_value = str(values.mode().iloc[0])
        counts = values.value_counts(dropna=True)
        if not counts.empty:
            top_count = int(counts.iloc[0])
        profile.append({
            'column': col,
            'type': str(values.dtype),
            'unique': int(values.nunique(dropna=True)),
            'top': top_value,
            'top_freq': top_count,
            'missing_pct': round(values.isna().mean() * 100, 2)
        })
    return profile


def get_data_summary(dataframe):
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = dataframe.select_dtypes(include=['object', 'category']).columns.tolist()
    total_missing = int(dataframe.isna().sum().sum())
    missing_pct = round(total_missing / (dataframe.shape[0] * dataframe.shape[1]) * 100, 2) if dataframe.size else 0
    top_missing = dataframe.isna().sum().sort_values(ascending=False).head(3).to_dict()
    return {
        'numeric_count': len(numeric_cols),
        'categorical_count': len(categorical_cols),
        'total_missing': total_missing,
        'missing_pct': missing_pct,
        'top_missing': top_missing,
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols
    }


def render_analysis_page(dataframe, sample_data=None):
    data_info = get_data_info(dataframe)
    data_profile = get_data_profile(dataframe)
    data_summary = get_data_summary(dataframe)
    plot_paths = generate_visualizations(dataframe)
    if sample_data is None:
        sample_data = dataframe.head(10).to_dict('records')
    return render_template('analysis.html',
                           data_info=data_info,
                           data_profile=data_profile,
                           data_summary=data_summary,
                           plot_paths=plot_paths,
                           sample_data=sample_data,
                           active_page='analysis')


@app.route('/analysis')
def analysis():
    global df
    if df is None:
        flash('No data available. Please upload a CSV file first.', 'error')
        return redirect(url_for('index'))
    return render_analysis_page(df)


@app.route('/transform', methods=['POST'])
def transform_data():
    global df

    if df is None:
        flash('No data to transform. Please upload a file first.')
        return redirect(url_for('index'))

    try:
        drop_columns = request.form.getlist('drop_columns')
        convert_column = request.form.get('convert_column')
        convert_type = request.form.get('convert_type')
        filter_column = request.form.get('filter_column')
        filter_operator = request.form.get('filter_operator')
        filter_value = request.form.get('filter_value')
        sample_size = request.form.get('sample_size')

        if drop_columns:
            df.drop(columns=drop_columns, inplace=True, errors='ignore')

        if convert_column and convert_type:
            if convert_type == 'numeric':
                df[convert_column] = pd.to_numeric(df[convert_column], errors='coerce')
            elif convert_type == 'datetime':
                df[convert_column] = pd.to_datetime(df[convert_column], errors='coerce')

        if filter_column and filter_operator and filter_value:
            if filter_operator == 'contains':
                df = df[df[filter_column].astype(str).str.contains(filter_value, na=False)]
            elif filter_operator == 'equals':
                df = df[df[filter_column].astype(str) == filter_value]
            elif filter_operator == 'greater':
                df = df[pd.to_numeric(df[filter_column], errors='coerce') > float(filter_value)]
            elif filter_operator == 'less':
                df = df[pd.to_numeric(df[filter_column], errors='coerce') < float(filter_value)]

        flash('Data transformation applied successfully!', 'success')

        data_info = get_data_info(df)
        data_profile = get_data_profile(df)
        plot_paths = generate_visualizations(df)
        sample_data = df.head(10).to_dict('records')
        if sample_size and sample_size.isdigit():
            sample_data = df.sample(min(int(sample_size), len(df)), random_state=1).to_dict('records')

        return render_template('analysis.html',
                               data_info=data_info,
                               data_profile=data_profile,
                               data_summary=get_data_summary(df),
                               plot_paths=plot_paths,
                               sample_data=sample_data,
                               active_page='analysis')
    except Exception as e:
        flash(f'Error transforming data: {str(e)}', 'error')
        return redirect(url_for('index'))


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
        data_info = get_data_info(df)
        data_profile = get_data_profile(df)
        
        # Generate new visualizations
        plot_paths = generate_visualizations(df)
        
        return render_template('analysis.html', 
                            data_info=data_info, 
                            data_profile=data_profile,
                            data_summary=get_data_summary(df),
                            plot_paths=plot_paths,
                            sample_data=df.head(10).to_dict('records'),
                            active_page='analysis')
    
    except Exception as e:
        flash(f'Error cleaning data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/auto-clean', methods=['POST'])
def auto_clean_data():
    global df
    if df is None:
        flash('No data to clean. Please upload a file first.', 'error')
        return redirect(url_for('index'))

    try:
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            if df[col].isna().any():
                df[col].fillna(df[col].mean(), inplace=True)

        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            if df[col].isna().any():
                df[col].fillna(df[col].mode()[0], inplace=True)

        flash('Auto clean applied successfully!', 'success')
        return render_analysis_page(df)
    except Exception as e:
        flash(f'Error applying auto clean: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/reset')
def reset_data():
    global df
    df = None
    flash('Dataset reset. Upload a new file to begin again.', 'success')
    return redirect(url_for('index'))

@app.route('/download')
def download_data():
    global df
    if df is not None:
        download_format = request.args.get('format', 'csv')

        if download_format == 'json':
            buffer = StringIO()
            buffer.write(df.to_json(orient='records', date_format='iso'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/json',
                as_attachment=True,
                download_name='cleaned_data.json'
            )

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
