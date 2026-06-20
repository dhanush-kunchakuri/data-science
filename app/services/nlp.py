import re


def interpret_query(dataframe, query_text):
    query = query_text.lower().strip()
    if 'highest' in query and 'month' in query:
        return highest_time_period(dataframe, query)
    if 'top performing' in query or 'best performing' in query:
        return top_category(dataframe, query)
    if 'anomaly' in query or 'outlier' in query:
        return detect_anomaly(dataframe)
    return {
        'query': query_text,
        'insight': 'Could not interpret the query automatically. Try using a dataset column name.'
    }


def highest_time_period(dataframe, query):
    # Example: look for date and numeric columns
    date_col = next((col for col in dataframe.columns if 'date' in col.lower()), None)
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    target_col = numeric_cols[-1] if numeric_cols else None
    if date_col and target_col:
        summary = dataframe.groupby(pd.to_datetime(dataframe[date_col], errors='coerce').dt.to_period('M'))[target_col].sum()
        best = summary.idxmax()
        return {
            'query': query,
            'result': f'Highest {target_col} month is {best} with {summary.max():,.2f}.'
        }
    return {'query': query, 'result': 'No suitable date and numeric columns found for this query.'}


def top_category(dataframe, query):
    category_cols = dataframe.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    if category_cols and numeric_cols:
        category = category_cols[0]
        value = numeric_cols[-1]
        best = dataframe.groupby(category)[value].sum().idxmax()
        return {
            'query': query,
            'result': f'Top performing category by {value} is {best}.'
        }
    return {'query': query, 'result': 'Could not determine top category from the dataset.'}


def detect_anomaly(dataframe):
    numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return {'query': 'anomaly', 'result': 'No numeric columns available for anomaly detection.'}
    col = numeric_cols[0]
    series = dataframe[col].dropna()
    if series.empty:
        return {'query': 'anomaly', 'result': 'No valid values available for anomaly detection.'}
    z_scores = (series - series.mean()) / series.std(ddof=0)
    outliers = series[abs(z_scores) > 3]
    return {
        'query': 'anomaly',
        'result': f'Found {len(outliers)} anomalies in {col}.'
    }
