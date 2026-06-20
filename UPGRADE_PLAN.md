# AI Analytics Platform Upgrade Plan

This document describes the upgraded architecture, folder structure, required libraries, and step-by-step implementation plan for transforming the existing data analytics dashboard into a production-level AI-powered analytics platform.

## 1. Target Architecture

### Frontend
- Flask + Jinja2 templates for core pages
- Bootstrap 5 for responsive UI and sidebar navigation
- Plotly.js for interactive charts and KPI cards
- Optional Dash pages for advanced analytics components
- JavaScript for smooth animations, loading states, and natural language query interface

### Backend
- Flask application server
- Flask-Login for authentication
- Flask-SQLAlchemy for user/session persistence
- Flask-Migrate for migrations
- Pandas / NumPy for data processing
- Scikit-learn for predictive analytics and NLP query classification
- Plotly for chart generation
- ReportLab / WeasyPrint for PDF report export

### Data + ML
- Dataset ingestion via CSV/Excel upload
- Data cleaning with missing value detection, duplicate removal, and outlier handling
- Insight generation using heuristic analytics and summary templates
- Forecasting using scikit-learn regression or time-series lag models
- Natural language query conversion to analysis commands
- Recommendation engine based on insight results

## 2. New Folder Structure

```
data-science/
├── app.py                      # Application entrypoint
├── config.py                   # Config and environment settings
├── requirements.txt            # Python dependencies
├── README.md
├── UPGRADE_PLAN.md             # Upgrade design doc
├── migrations/                 # Database migrations
├── app/                        # Flask application package
│   ├── __init__.py
│   ├── models.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── services/
│   │   ├── data_loader.py
│   │   ├── cleaners.py
│   │   ├── summarizer.py
│   │   ├── insights.py
│   │   ├── forecasting.py
│   │   ├── nlp.py
│   │   ├── recommendations.py
│   │   ├── reports.py
│   │   └── utils.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── analysis.html
│   │   ├── report.html
│   │   └── sessions.html
│   └── static/
│       ├── css/style.css
│       ├── js/dashboard.js
│       └── images/
├── notebooks/                  # Exploratory notebooks
├── static/                     # Legacy static assets (optional)
├── templates/                  # Legacy templates (optional)
└── uploads/                    # Uploaded dataset files
```

## 3. Required Libraries

- Flask==2.3.3
- Flask-Login==0.6.2
- Flask-Migrate==4.0.4
- Flask-SQLAlchemy==3.0.6
- pandas>=2.0.0
- numpy>=1.24.0
- scikit-learn>=1.2.0
- plotly>=5.18.0
- reportlab>=4.0.0
- python-dotenv>=1.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- dash>=2.14.1
- dash-bootstrap-components>=1.5.0
- itsdangerous>=2.1.2
- Werkzeug>=2.3.0

Optional (for advanced NLP or PDF workflows):
- spacy>=3.5.0
- weasyprint>=57.1
- openai>=1.5.0

## 4. Implementation Plan

### Phase 1: Project Restructure and Authentication
1. Create `app/` package and move current core logic into modular service files.
2. Add `config.py` to manage secrets, upload path, database URI, and app mode.
3. Create `models.py` for `User`, `UploadSession`, and `DatasetSession`.
4. Add authentication routes in `auth.py`.
5. Add user session persistence and upload history.
6. Implement login/register pages and session-based access control.

### Phase 2: Data Ingestion and Cleaning Module
1. Build `app/services/data_loader.py` to parse CSV/Excel safely.
2. Build `app/services/cleaners.py` with:
   - `detect_missing_values`
   - `remove_duplicates`
   - `handle_outliers` (IQR and Z-score)
   - `fill_missing_values`
3. Add `get_data_quality_report()` to summarize before/after state.
4. Add UI controls for cleaning strategies and preview effects.

### Phase 3: AI Insights Generator
1. Build `app/services/insights.py` to generate:
   - dataset overview
   - key trends
   - anomalies
   - top KPIs
2. Use numeric heuristics and `describe()` plus change detection to create readable summaries.
3. Add an AI insight panel to the dashboard with cards and text blocks.

### Phase 4: Predictive Analytics
1. Build `app/services/forecasting.py`.
2. Support:
   - time-series forecasting for date-indexed data
   - regression forecasting for selected numeric target
3. Provide train/test split, model fit, prediction graph data, and accuracy metrics.
4. Add UI to select target/time columns and forecast horizon.

### Phase 5: Natural Language Query
1. Build `app/services/nlp.py`.
2. Implement:
   - query intent recognition
   - entity extraction for columns and date ranges
   - rule-based mapping for common business questions
3. Map queries like:
   - "Show highest sales month"
   - "Find top performing category"
   - "What are the slow-moving products?"
4. Return analysis results, chart specification, and summary text.

### Phase 6: Smart Recommendations
1. Build `app/services/recommendations.py`.
2. Generate action items from insights, e.g.:
   - "Increase stock in Region A"
   - "Reduce spending on Category B"
3. Use threshold rules for anomalies and trend direction.
4. Display recommendations as cards with confidence levels.

### Phase 7: Advanced Visualizations and UI
1. Add KPI cards and summary ribbons on dashboard.
2. Add Plotly visualizations for:
   - trend analysis
   - correlation matrix
   - heatmaps
   - top categories and drill-down filters
3. Add dark/light mode support and responsive sidebar.
4. Add loading indicators and animation states in `static/js/dashboard.js`.

### Phase 8: Export Reports and Session Management
1. Build `app/services/reports.py` for PDF and CSV export.
2. Add report templates with charts and AI insights.
3. Implement session save/load for previous uploads.
4. Add `sessions.html` to browse stored dashboards.

### Phase 9: Performance and Production Hardening
1. Add file size validation and chunked CSV loading.
2. Cache intermediate summaries and chart data in session or Redis.
3. Add error handling for invalid files and unsupported columns.
4. Add unit tests for data cleaning, forecasting, and NLP query mapping.
5. Prepare deployment with `gunicorn` and environment variables.

## 5. Step-by-Step Code Changes

### 5.1 Existing files
- `app.py`: replace monolithic app with a structured factory and route registration.
- `dashboard.py`: preserve useful dashboard components, then migrate interactive Plotly logic into `app/services` and frontend JS.
- `templates/`: keep current pages as reference, then build `app/templates` with new pages.
- `static/css/style.css`: preserve styling ideas and extend for modern cards and theme toggles.

### 5.2 New files to add
- `config.py`
- `app/__init__.py`
- `app/models.py`
- `app/auth.py`
- `app/dashboard.py`
- `app/services/data_loader.py`
- `app/services/cleaners.py`
- `app/services/summarizer.py`
- `app/services/insights.py`
- `app/services/forecasting.py`
- `app/services/nlp.py`
- `app/services/recommendations.py`
- `app/services/reports.py`
- `app/static/js/dashboard.js`
- `app/templates/login.html`
- `app/templates/register.html`
- `app/templates/dashboard.html`
- `app/templates/sessions.html`

### 5.3 Example service responsibilities
- `data_loader.py`: parse uploads, infer dtypes, build safe dataframe
- `cleaners.py`: detect missing, duplicates, outliers, with `before_after_summary`
- `insights.py`: create KPI cards, top trends, anomalies, correlation signals
- `forecasting.py`: generate predictions using `scikit-learn`
- `nlp.py`: classify query intent and build analysis commands
- `recommendations.py`: map insights to action items
- `reports.py`: export CSV / PDF containing charts and summary text

### 5.4 Backend route flow
- `/` => landing page + upload
- `/login`, `/register`
- `/dashboard` => main analytics workspace
- `/upload` => handle file upload
- `/clean` => execute cleaning operations
- `/forecast` => run predictive model and return chart data
- `/query` => accept natural language questions
- `/recommend` => fetch recommendations
- `/export/pdf` and `/export/csv`
- `/sessions` => list saved datasets

## 6. Clean and Modular Design Notes

- Keep all data science logic inside `app/services/*`
- Keep route handlers thin and focused on request/response
- Keep UI templates declarative and chart-driven
- Use session and database storage only for metadata and user history
- Avoid global variables; persist active dataset via secure session IDs and storage files
- Provide small reusable utilities for summary stats and chart generation

---

This upgrade plan is designed to convert the current proof-of-concept into a maintainable data analytics platform with AI-driven insights, forecasting, natural language query, and user session management.
