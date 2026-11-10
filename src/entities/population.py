from dataclasses import dataclass
from math import isclose, isfinite
from numbers import Real


@dataclass
class Population:
    """Initial population counts in the SEIR compartments."""

    total: float
    susceptible: float
    exposed: float
    infected: float
    recovered: float

    def __post_init__(self):
        for field_name in (
            "total",
            "susceptible",
            "exposed",
            "infected",
            "recovered",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"{field_name} must be a finite number.")
            if not isfinite(value):
                raise ValueError(f"{field_name} must be a finite number.")

        if self.total <= 0:
            raise ValueError("Population total must be positive.")

        if min(self.susceptible, self.exposed, self.infected, self.recovered) < 0:
            raise ValueError("Population compartments must be non-negative.")

        compartments = (
            self.susceptible
            + self.exposed
            + self.infected
            + self.recovered
        )

        if not isclose(compartments, self.total, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("Compartments must sum to the population total.")