from dataclasses import dataclass
from math import isfinite

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True, slots=True, eq=False)
class SimulationResult:
    """Immutable time series and metadata produced by a simulation."""

    days: ArrayLike
    susceptible: ArrayLike
    exposed: ArrayLike
    infected: ArrayLike
    recovered: ArrayLike
    model_name: str
    scenario_name: str

    def __post_init__(self) -> None:
        if not isinstance(self.model_name, str) or not self.model_name.strip():
            raise ValueError("model_name must not be empty.")
        if not isinstance(self.scenario_name, str) or not self.scenario_name.strip():
            raise ValueError("scenario_name must not be empty.")

        names = ("days", "susceptible", "exposed", "infected", "recovered")
        series_sizes: set[int] = set()
        for name in names:
            try:
                values = np.asarray(getattr(self, name), dtype=np.float64)
            except (TypeError, ValueError) as error:
                raise TypeError(f"{name} must be a one-dimensional numeric series.") from error

            if values.ndim != 1:
                raise ValueError(f"{name} must be one-dimensional.")
            if values.size == 0:
                raise ValueError("Simulation result series must not be empty.")
            if not np.isfinite(values).all():
                raise ValueError(f"{name} must contain only finite values.")

            immutable = np.frombuffer(values.tobytes(), dtype=np.float64)
            object.__setattr__(self, name, immutable)
            series_sizes.add(immutable.size)

        if len(series_sizes) != 1:
            raise ValueError("All simulation result series must have the same size.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimulationResult):
            return NotImplemented
        return (
            self.model_name == other.model_name
            and self.scenario_name == other.scenario_name
            and all(
                np.array_equal(getattr(self, name), getattr(other, name))
                for name in ("days", "susceptible", "exposed", "infected", "recovered")
            )
        )

        object.__setattr__(self, "_series", tuple(series))