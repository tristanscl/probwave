from ._model import Model
import numpy as np
import pandas as pd
import datetime as dt


class GBM(Model):
    def fit(self, data: pd.Series) -> None:
        self.mu: float
        self.sigma: float
        self.X0: float
        self.date: dt.date

        returns = data / data.shift(1) - 1
        self.mu = returns.mean()
        self.sigma = returns.std()
        self.X0 = data.dropna().iloc[-1]
        self.date = data.dropna().index[-1]  # type: ignore

    def sample(self, n_days: int, n_sim: int) -> np.ndarray:
        Rt = np.random.normal(self.mu, self.sigma, size=[n_sim, n_days])
        Xt = self.X0 * np.cumprod(Rt + 1, axis=1)
        return Xt
