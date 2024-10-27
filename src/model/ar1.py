from ._model import Model
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import datetime as dt


class AR1(Model):
    def fit(self, data: pd.Series) -> None:
        self.X0: float
        self.a: LinearRegression
        self.phi: LinearRegression
        self.epsilon: float
        self.date: dt.date

        num_data: np.ndarray = data.dropna().to_numpy()
        self.X0 = num_data[-1]
        num_data /= self.X0
        num_data = np.log(num_data)
        past_time = np.arange(-num_data.size, 0).reshape(-1, 1)
        self.a = LinearRegression(fit_intercept=False)
        self.a.fit(past_time, num_data)
        self.phi = LinearRegression(fit_intercept=False)
        pre = num_data[:-1].reshape(-1, 1)
        post = num_data[1:].reshape(-1, 1)
        self.phi.fit(pre, post)
        res = post - self.phi.predict(pre)
        self.epsilon = np.std(res)  # type: ignore
        self.date = data.dropna().index[-1]  # type: ignore

    def sample(self, n_days: int, n_sim: int) -> np.ndarray:
        Yt = np.zeros([n_sim, n_days])
        for t in range(n_days - 1):
            Yt[:, t + 1] = self.phi.predict(Yt[:, t].reshape(-1, 1)).reshape(
                -1
            ) + self.epsilon * np.random.normal(size=n_sim)
        future_time = np.arange(n_days).reshape(-1, 1)
        logXt_X0 = Yt + self.a.predict(future_time)
        Xt = self.X0 * np.exp(logXt_X0)
        return Xt
