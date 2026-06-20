import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def parse_upload(file_storage):
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        return None, filename, 'Unsupported file type. Please upload CSV or Excel.'

    try:
        if filename.lower().endswith('.csv'):
            dataframe = pd.read_csv(file_storage)
        else:
            dataframe = pd.read_excel(file_storage)
        return dataframe, filename, None
    except Exception as exc:
        return None, filename, f'Error reading file: {exc}'
