import pandas as pd


def detect_missing(dataframe):
    return dataframe.isnull().sum().to_dict()


def detect_duplicates(dataframe):
    return int(dataframe.duplicated().sum())


def detect_outliers(dataframe, method='iqr'):
    outlier_counts = {}
    numeric_cols = dataframe.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        series = dataframe[col].dropna()
        if method == 'iqr':
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_counts[col] = int(((series < lower) | (series > upper)).sum())
        else:
            outlier_counts[col] = 0
    return outlier_counts


def remove_duplicates(dataframe):
    return dataframe.drop_duplicates(), int(dataframe.duplicated().sum())


def fill_missing(dataframe, strategy='mean'):
    df = dataframe.copy()
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype.kind in 'biufc':
                if strategy == 'median':
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == 'mode':
                    df[col] = df[col].fillna(df[col].mode().iloc[0])
                else:
                    df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else '')
    return df


def generate_quality_report(dataframe):
    return {
        'shape': dataframe.shape,
        'missing': detect_missing(dataframe),
        'duplicates': detect_duplicates(dataframe),
        'outliers': detect_outliers(dataframe),
        'columns': dataframe.columns.tolist(),
        'dtypes': dataframe.dtypes.astype(str).to_dict()
    }


def apply_cleaning_steps(dataframe, drop_na_cols=None, fill_strategy='mean', remove_duplicates_flag=True, outlier_method='iqr'):
    before = generate_quality_report(dataframe)
    df = dataframe.copy()
    if drop_na_cols:
        df = df.dropna(subset=drop_na_cols)
    if remove_duplicates_flag:
        df = df.drop_duplicates()
    if fill_strategy:
        df = fill_missing(df, fill_strategy)
    after = generate_quality_report(df)
    return df, {'before': before, 'after': after}
