import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
from flask import Flask, send_from_directory
from datetime import datetime

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create uploads directory if it doesn't exist
UPLOAD_DIRECTORY = "uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Data Analysis Dashboard", className="text-center my-4"), width=12)
    ]),
    
    # File Upload Section
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select a CSV File')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
        ], width=12)
    ]),
    
    # Data Summary Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Rows", className="card-title"),
                    html.H4(id="row-count", className="card-text text-center")
                ])
            ], className="mb-4")
        ], md=3, sm=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Columns", className="card-title"),
                    html.H4(id="col-count", className="card-text text-center")
                ])
            ], className="mb-4")
        ], md=3, sm=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Missing Values", className="card-title"),
                    html.H4(id="missing-values", className="card-text text-center")
                ])
            ], className="mb-4")
        ], md=3, sm=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("File Type", className="card-title"),
                    html.H4("CSV", className="card-text text-center")
                ])
            ], className="mb-4")
        ], md=3, sm=6, xs=12),
    ]),
    
    # Tabs for different visualizations
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Data Preview", tab_id="tab-preview"),
                dbc.Tab(label="Statistics", tab_id="tab-stats"),
                dbc.Tab(label="Visualizations", tab_id="tab-viz"),
                dbc.Tab(label="Correlation", tab_id="tab-corr")
            ], id="tabs", active_tab="tab-preview"),
            html.Div(id="tab-content", className="p-4 border border-top-0")
        ], width=12)
    ]),
    
    # Store the uploaded data
    dcc.Store(id='stored-data')
], fluid=True)

# Helper function to parse uploaded file
def parse_contents(contents, filename):
    import base64
    import io
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file format. Please upload a CSV or Excel file."
            
        return df, ""
    except Exception as e:
        return None, f"There was an error processing this file: {str(e)}"

# Callback to handle file upload and update data store
@app.callback(
    [Output('stored-data', 'data'),
     Output('row-count', 'children'),
     Output('col-count', 'children'),
     Output('missing-values', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return None, "-", "-", "-"
    
    df, error = parse_contents(contents, filename)
    if error:
        return None, "Error", "Error", "Error"
    
    # Save the uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(UPLOAD_DIRECTORY, f"{timestamp}_{filename}")
    df.to_csv(save_path, index=False)
    
    # Calculate statistics
    row_count = f"{len(df):,}"
    col_count = f"{len(df.columns)}"
    missing_values = f"{df.isnull().sum().sum():,}"
    
    return df.to_dict('records'), row_count, col_count, missing_values

# Callback to update tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab'),
     Input('stored-data', 'data')]
)
def render_tab_content(active_tab, data):
    if data is None:
        return html.Div("Please upload a CSV file to begin analysis.")
    
    df = pd.DataFrame(data)
    
    if active_tab == "tab-preview":
        return html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'height': 'auto',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left',
                    'padding': '8px'
                }
            )
        ])
        
    elif active_tab == "tab-stats":
        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = df[numeric_cols].describe().reset_index()
        
        return html.Div([
            html.H5("Descriptive Statistics", className="mb-3"),
            dash_table.DataTable(
                data=stats.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in stats.columns],
                page_size=10,
                style_table={'overflowX': 'auto'}
            )
        ])
        
    elif active_tab == "tab-viz":
        # Visualization options
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) == 0:
            return html.Div("No numeric columns found for visualization.")
            
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Select X-Axis"),
                    dcc.Dropdown(
                        id='x-axis',
                        options=[{'label': col, 'value': col} for col in numeric_cols],
                        value=numeric_cols[0] if len(numeric_cols) > 0 else None
                    )
                ], md=6),
                
                dbc.Col([
                    html.Label("Select Y-Axis"),
                    dcc.Dropdown(
                        id='y-axis',
                        options=[{'label': col, 'value': col} for col in numeric_cols],
                        value=numeric_cols[1] if len(numeric_cols) > 1 else None
                    )
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='scatter-plot')
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='histogram')
                ], width=12)
            ])
        ])
        
    elif active_tab == "tab-corr":
        # Correlation heatmap
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return html.Div("Not enough numeric columns for correlation analysis.")
            
        corr = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr,
            labels=dict(x="Features", y="Features", color="Correlation"),
            x=corr.columns,
            y=corr.columns,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1
        )
        
        fig.update_layout(
            title='Correlation Heatmap',
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            yaxis_autorange='reversed',
            width=800,
            height=700
        )
        
        return dcc.Graph(figure=fig)

# Callback for scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-axis', 'value'),
     Input('y-axis', 'value'),
     Input('stored-data', 'data')]
)
def update_scatter_plot(x_col, y_col, data):
    if data is None or x_col is None or y_col is None:
        return {}
    
    df = pd.DataFrame(data)
    
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col,
        title=f"{y_col} vs {x_col}",
        trendline="ols"
    )
    
    return fig

# Callback for histogram
@app.callback(
    Output('histogram', 'figure'),
    [Input('x-axis', 'value'),
     Input('stored-data', 'data')]
)
def update_histogram(x_col, data):
    if data is None or x_col is None:
        return {}
    
    df = pd.DataFrame(data)
    
    fig = px.histogram(
        df, 
        x=x_col,
        title=f"Distribution of {x_col}",
        marginal="box"
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
