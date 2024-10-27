import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def fit(self, data: pd.Series) -> None:
        pass

    @abstractmethod
    def sample(self, n_days: int, n_sim: int) -> np.ndarray:
        pass
