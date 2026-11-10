from numbers import Real

import numpy as np
from scipy.integrate import solve_ivp

from src.entities.scenario import Scenario
from src.models.base import EpidemiologicalModel
from src.simulation.result import SimulationResult


class SEIRModel(EpidemiologicalModel):
    """Deterministic SEIR model for a closed, well-mixed population.

    The model assumes constant transmission and transition rates, no births or
    deaths, and homogeneous mixing. Exposed individuals are not infectious.
    A configured beta overrides ``Disease.transmission_rate``.
    """

    def __init__(self, beta: float | None = None) -> None:
        if beta is not None:
            if isinstance(beta, bool) or not isinstance(beta, Real):
                raise TypeError("beta must be a finite non-negative number")
            if not np.isfinite(beta) or beta < 0:
                raise ValueError("beta must be a finite non-negative number")

        self.beta = float(beta) if beta is not None else None

    def simulate(self, scenario: Scenario) -> SimulationResult:
        """Solve the SEIR equations and return daily compartment values.

        Interventions are not part of this baseline model and are rejected
        rather than silently ignored.
        """
        if not isinstance(scenario, Scenario):
            raise TypeError("scenario must be a Scenario instance")
        if scenario.interventions:
            raise NotImplementedError(
                "The baseline SEIR model does not apply interventions."
            )

        population = scenario.population
        disease = scenario.disease
        total = float(population.total)
        beta = (
            self.beta
            if self.beta is not None
            else float(disease.transmission_rate)
        )
        sigma = 1.0 / float(disease.latent_period)
        gamma = 1.0 / float(disease.infectious_period)
        initial = np.asarray(
            [
                population.susceptible,
                population.exposed,
                population.infected,
                population.recovered,
            ],
            dtype=float,
        )

        def equations(_time: float, state: np.ndarray) -> tuple[float, ...]:
            susceptible, exposed, infectious, recovered = state
            infection = beta * susceptible * infectious / total
            progression = sigma * exposed
            recovery = gamma * infectious
            return (
                -infection,
                infection - progression,
                progression - recovery,
                recovery,
            )

        duration = float(scenario.duration)
        days = np.append(np.arange(0.0, duration, 1.0), duration)
        solution = solve_ivp(
            equations,
            (0.0, duration),
            initial,
            t_eval=days,
            method="RK45",
            rtol=1e-8,
            atol=1e-9,
        )

        if not solution.success:
            raise RuntimeError(f"SEIR integration failed: {solution.message}")
        if solution.y.shape != (4, days.size) or not np.isfinite(solution.y).all():
            raise RuntimeError("SEIR integration returned invalid numerical values")

        negative_tolerance = max(1e-8, total * 1e-10)
        if np.any(solution.y < -negative_tolerance):
            raise RuntimeError("SEIR integration produced negative compartments")

        mass_tolerance = max(1e-8, total * 1e-10)
        if not np.allclose(
            solution.y.sum(axis=0),
            total,
            rtol=1e-8,
            atol=mass_tolerance,
        ):
            raise RuntimeError("SEIR integration did not conserve population")

        return SimulationResult(
            days=solution.t,
            susceptible=solution.y[0],
            exposed=solution.y[1],
            infected=solution.y[2],
            recovered=solution.y[3],
            model_name=type(self).__name__,
            scenario_name=scenario.name,
        )