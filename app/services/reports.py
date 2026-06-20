import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import current_app, send_file
import pandas as pd


def export_csv_report(dataframe):
    filename = 'exported_data.csv'
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    dataframe.to_csv(path, index=False)
    return send_file(path, as_attachment=True, download_name=filename)


def build_pdf_report(dataframe, user_email):
    filename = f'report_{user_email.replace("@", "_")}.pdf'
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 50, 'AI Analytics Report')
    c.setFont('Helvetica', 10)
    c.drawString(40, height - 80, f'Generated for {user_email}')
    c.drawString(40, height - 100, f'Record count: {len(dataframe)}')
    c.drawString(40, height - 120, f'Column count: {len(dataframe.columns)}')
    c.save()
    return path
