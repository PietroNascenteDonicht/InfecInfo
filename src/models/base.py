from abc import ABC, abstractmethod

from src.entities.scenario import Scenario
from src.simulation.result import SimulationResult


class EpidemiologicalModel(ABC):
    """Interface for epidemiological models that simulate a scenario."""

    @abstractmethod
    def simulate(self, scenario: Scenario) -> SimulationResult:
        """Run the model for ``scenario`` and return its time series."""
        raise NotImplementedError