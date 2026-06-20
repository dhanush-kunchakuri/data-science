import pandas as pd
from .cleaners import generate_quality_report


def top_kpis(dataframe, top_n=5):
    numeric_cols = dataframe.select_dtypes(include=['number']).columns
    kpis = []
    for col in numeric_cols:
        series = dataframe[col].dropna()
        kpis.append({
            'name': col,
            'mean': round(series.mean(), 2) if not series.empty else None,
            'median': round(series.median(), 2) if not series.empty else None,
            'max': round(series.max(), 2) if not series.empty else None,
            'min': round(series.min(), 2) if not series.empty else None,
            'std': round(series.std(), 2) if not series.empty else None,
        })
    return kpis[:top_n]


def generate_insight_blocks(dataframe):
    insights = []
    if dataframe.empty:
        return insights

    numeric_cols = dataframe.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        total_rows = len(dataframe)
        insights.append({
            'title': 'Dataset size',
            'detail': f'{total_rows} rows and {len(dataframe.columns)} columns loaded.'
        })

    for col in numeric_cols[:3]:
        series = dataframe[col].dropna()
        if not series.empty:
            recent_trend = 'increasing' if series.iloc[-1] > series.iloc[0] else 'decreasing'
            insights.append({
                'title': f'{col} trend',
                'detail': f'{col} has a {recent_trend} trend from first to last record.'
            })

    if len(numeric_cols) > 1:
        corr = dataframe[numeric_cols].corr().abs()
        high_corr = corr.stack().sort_values(ascending=False).drop_duplicates()
        if not high_corr.empty:
            top_pair = high_corr.index[1] if len(high_corr) > 1 else high_corr.index[0]
            insights.append({
                'title': 'Strong correlation',
                'detail': f'{top_pair[0]} and {top_pair[1]} are highly correlated.'
            })

    return insights


def generate_insights(dataframe):
    return {
        'profile': generate_quality_report(dataframe) if 'generate_quality_report' in globals() else {},
        'kpis': top_kpis(dataframe),
        'insight_cards': generate_insight_blocks(dataframe)
    }
