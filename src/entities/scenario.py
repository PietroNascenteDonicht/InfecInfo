from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from src.entities.disease import Disease
from src.entities.population import Population


@dataclass
class Scenario:
    """Configuration and initial state for one simulation run."""

    name: str
    disease: Disease
    population: Population
    duration: float
    interventions: list[object] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Scenario name must not be empty.")
        if not isinstance(self.disease, Disease):
            raise TypeError("disease must be a Disease instance.")
        if not isinstance(self.population, Population):
            raise TypeError("population must be a Population instance.")
        if isinstance(self.duration, bool) or not isinstance(self.duration, Real):
            raise TypeError("duration must be a finite positive number of days.")
        if not isfinite(self.duration) or self.duration <= 0:
            raise ValueError("Scenario duration must be finite and positive.")
        if not isinstance(self.interventions, list):
            raise TypeError("interventions must be a list.")

        self.interventions = list(self.interventions)