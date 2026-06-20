from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from .services.data_loader import parse_upload
from .services.cleaners import generate_quality_report, apply_cleaning_steps
from .services.insights import generate_insights
from .services.forecasting import run_forecast
from .services.nlp import interpret_query
from .services.recommendations import generate_recommendations
from .services.reports import build_pdf_report, export_csv_report
from .models import UploadSession
from . import db
import pandas as pd


dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard_bp.route('/')
def index():
    return render_template('index.html')


@dashboard_bp.route('/dashboard')
@login_required
def home():
    sessions = UploadSession.query.filter_by(user_id=current_user.id).order_by(UploadSession.uploaded_at.desc()).all()
    return render_template('dashboard.html', sessions=sessions)


@dashboard_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get('file')
    if not file:
        flash('No file selected for upload.', 'warning')
        return redirect(url_for('dashboard.home'))

    dataframe, filename, error = parse_upload(file)
    if error:
        flash(error, 'danger')
        return redirect(url_for('dashboard.home'))

    session['dataframe'] = dataframe.to_dict('records')
    session['filename'] = filename
    summary = generate_quality_report(dataframe)
    session['summary'] = summary

    upload_record = UploadSession(
        user_id=current_user.id,
        filename=filename,
        dataset_summary=summary
    )
    db.session.add(upload_record)
    db.session.commit()

    return redirect(url_for('dashboard.analysis'))


@dashboard_bp.route('/analysis')
@login_required
def analysis():
    data = session.get('dataframe')
    if not data:
        flash('Please upload a dataset first.', 'warning')
        return redirect(url_for('dashboard.home'))

    df = pd.DataFrame(data)
    insights = generate_insights(df)
    return render_template('analysis.html', data=insights)


@dashboard_bp.route('/forecast', methods=['POST'])
@login_required
def forecast():
    # Implement forecast route logic
    return redirect(url_for('dashboard.analysis'))


@dashboard_bp.route('/query', methods=['POST'])
@login_required
def query():
    question = request.form.get('query_text', '')
    data = session.get('dataframe')
    if not data:
        flash('Please upload a dataset before asking questions.', 'warning')
        return redirect(url_for('dashboard.home'))

    df = pd.DataFrame(data)
    result = interpret_query(df, question)
    session['query_result'] = result
    return redirect(url_for('dashboard.analysis'))


@dashboard_bp.route('/export/pdf')
@login_required
def export_pdf():
    data = session.get('dataframe')
    if not data:
        flash('No dataset available to export.', 'warning')
        return redirect(url_for('dashboard.analysis'))

    pdf_path = build_pdf_report(pd.DataFrame(data), current_user.email)
    return send_file(pdf_path, as_attachment=True)


@dashboard_bp.route('/export/csv')
@login_required
def export_csv():
    data = session.get('dataframe')
    if not data:
        flash('No dataset available to export.', 'warning')
        return redirect(url_for('dashboard.analysis'))

    return export_csv_report(pd.DataFrame(data))
