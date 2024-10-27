import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import yfinance as yf


def prob_wave_plot(
    sim: np.ndarray,
    sim_start_date: dt.date,
    data: pd.Series,
    cur: str,
    n_levels: int = 10,
    n_sim_plot: int = 5,
    alpha_sim_plot: float = 0.3,
) -> None:
    # plotting the data
    plt.plot(data.index, data, label="data")

    # plotting the prob wave
    sim_dates = pd.date_range(start=sim_start_date, periods=sim.shape[1], freq="B")
    for q in np.linspace(1 / n_levels, 1 / 2, n_levels):
        lower_quantile = np.quantile(sim, q=q, axis=0)
        upper_quantile = np.quantile(sim, q=1 - q, axis=0)
        plt.fill_between(
            sim_dates, lower_quantile, upper_quantile, color="gray", alpha=2 / n_levels
        )

    # plotting some samples
    for i in range(n_sim_plot):
        plt.plot(sim_dates, sim[i], alpha=alpha_sim_plot)

    plt.title("Forecast - " + data.name)  # type: ignore
    plt.legend()
    plt.grid()
    plt.ylabel(cur)
    plt.xticks(rotation=45)
    plt.tight_layout()
