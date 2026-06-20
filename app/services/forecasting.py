import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def prepare_time_series(dataframe, target_column, date_column=None):
    df = dataframe.copy()
    if date_column is not None:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.sort_values(date_column)
        df = df.dropna(subset=[date_column, target_column])
        df = df.set_index(date_column)
    else:
        df = df.dropna(subset=[target_column])
    return df


def create_lag_features(series, n_lags=3):
    df = pd.DataFrame({
        'target': series
    })
    for lag in range(1, n_lags + 1):
        df[f'lag_{lag}'] = df['target'].shift(lag)
    return df.dropna()


def run_forecast(dataframe, target_column, horizon=12, date_column=None):
    df = prepare_time_series(dataframe, target_column, date_column)
    if df.empty or target_column not in df.columns:
        return None

    data = create_lag_features(df[target_column])
    X = data.drop(columns=['target'])
    y = data['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics = {
        'rmse': round(np.sqrt(mean_squared_error(y_test, predictions)), 4),
        'r2': round(r2_score(y_test, predictions), 4)
    }

    forecast_index = pd.date_range(start=X_test.index[-1] + pd.Timedelta(days=1), periods=horizon, freq='D')
    future_features = np.tile(X_test.iloc[-1].values, (horizon, 1))
    forecast = model.predict(future_features)

    return {
        'metrics': metrics,
        'predictions': list(map(float, forecast)),
        'prediction_index': list(forecast_index.strftime('%Y-%m-%d'))
    }
