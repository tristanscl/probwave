import yfinance as yf
import pandas as pd
import datetime as dt


def get_data(asset: str, start: dt.date, end: dt.date) -> pd.Series:
    data = yf.Ticker(asset).history(start=start, end=end)["Close"]
    data.name = asset
    return data


def clean_data(data: pd.Series) -> pd.Series:
    data = data.copy()
    data.index = data.index.date  # type: ignore
    start: dt.date = data.index[0]  # type: ignore
    end: dt.date = data.index[-1]  # type: ignore
    all_dates = pd.date_range(start=start, end=end, freq="D").date
    clean_dates = pd.date_range(start=start, end=end, freq="B").date
    return data.reindex(all_dates).ffill().reindex(clean_dates)


def convert_data(data: pd.Series, cur: str) -> pd.Series:
    data = data.copy()
    asset_cur = yf.Ticker(data.name).info["currency"]
    if asset_cur != cur:
        change = yf.Ticker(cur + asset_cur + "=X").history(
            start=data.index[0], end=data.index[-1]
        )["Close"]
        change = clean_data(change)
        data /= change
    return data


def unsplit(
    data: pd.Series,
    upper_threshold: float = 1.8,
    lower_threshold: float = 0.6,
    verbose: bool = False,
) -> pd.Series:
    """
    Adjusts the closing prices series for stock splits with configurable thresholds and optional logging.

    Parameters:
    prices (pd.Series): A pandas Series of closing prices, indexed by dates (dt.date).
    upper_threshold (float): Threshold for detecting a regular stock split (default is 1.8).
    lower_threshold (float): Threshold for detecting a reverse stock split (default is 0.6).
    verbose (bool): If True, prints messages when a split is detected (default is False).

    Returns:
    pd.Series: The adjusted closing prices with historical prices corrected for splits.
    """
    # Création d'une copie pour ajustement
    adjusted_prices = data.copy()

    # Boucle de détection et correction de split
    for i in range(1, len(data)):
        # Calcul du ratio entre les prix du jour précédent et du jour actuel
        ratio = adjusted_prices.iloc[i - 1] / adjusted_prices.iloc[i]

        # Détection de split classique
        if ratio > upper_threshold:
            factor = round(ratio)
            adjusted_prices.iloc[:i] = adjusted_prices.iloc[:i] / factor
            if verbose:
                print(
                    f"Regular stock split detected on {adjusted_prices.index[i]} with a factor of {factor}:1."
                )

        # Détection de split inverse
        elif ratio < lower_threshold:
            factor = round(1 / ratio)
            adjusted_prices.iloc[:i] = adjusted_prices.iloc[:i] * factor
            if verbose:
                print(
                    f"Reverse stock split detected on {adjusted_prices.index[i]} with a factor of 1:{factor}."
                )

    return adjusted_prices
