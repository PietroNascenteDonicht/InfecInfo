import numpy as np
import pytest

from src.entities.disease import Disease
from src.entities.population import Population
from src.entities.scenario import Scenario
from src.models.base import EpidemiologicalModel
from src.models.seir import SEIRModel
from src.simulation.result import SimulationResult


def make_disease(**overrides: object) -> Disease:
    values = {
        "name": "Synthetic disease",
        "transmission_type": "unspecified",
        "transmission_rate": 0.25,
        "symptomatic_rate": 0.6,
        "asymptomatic_rate": 0.4,
        "incubation_period": 4.0,
        "infectious_period": 5.0,
        "latent_period": 2.0,
        "severity": 0.1,
    }
    values.update(overrides)
    return Disease(**values)


def make_population(
    susceptible: float = 990,
    exposed: float = 0,
    infected: float = 10,
    recovered: float = 0,
) -> Population:
    compartments = (susceptible, exposed, infected, recovered)
    return Population(sum(compartments), *compartments)


def make_scenario(
    population: Population | None = None,
    interventions: list[object] | None = None,
) -> Scenario:
    return Scenario(
        "Test scenario",
        make_disease(),
        population or make_population(),
        30,
        [] if interventions is None else interventions,
    )


def test_disease_accepts_valid_characteristics_and_separate_fatality_measures():
    disease = make_disease(
        case_fatality_ratio=0.02,
        infection_fatality_ratio=0.01,
    )

    assert disease.latent_period == 2.0
    assert disease.incubation_period == 4.0
    assert disease.case_fatality_ratio == 0.02
    assert disease.infection_fatality_ratio == 0.01


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("name", " ", ValueError),
        ("transmission_rate", -0.1, ValueError),
        ("transmission_rate", float("nan"), ValueError),
        ("incubation_period", 0, ValueError),
        ("latent_period", -1, ValueError),
        ("infectious_period", float("inf"), ValueError),
        ("severity", 1.1, ValueError),
        ("symptomatic_rate", -0.1, ValueError),
        ("case_fatality_ratio", 1.1, ValueError),
        ("infection_fatality_ratio", -0.1, ValueError),
        ("severity", "high", TypeError),
    ],
)
def test_disease_rejects_invalid_values(
    field: str, value: object, error: type[Exception]
):
    with pytest.raises(error):
        make_disease(**{field: value})


def test_population_accepts_valid_integer_and_fractional_counts():
    population = Population(10.5, 8.0, 1.0, 1.0, 0.5)

    assert population.total == 10.5


@pytest.mark.parametrize(
    "values",
    [
        (0, 0, 0, 0, 0),
        (10, 8, 1, 1, 1),
        (10, 11, -1, 0, 0),
        (10, float("nan"), 0, 0, 0),
        (10, True, 0, 0, 9),
    ],
)
def test_population_rejects_invalid_totals_or_compartments(
    values: tuple[object, ...],
):
    with pytest.raises((TypeError, ValueError)):
        Population(*values)


def test_scenario_validates_inputs_and_copies_intervention_list():
    interventions = ["not implemented"]
    scenario = make_scenario(interventions=interventions)
    other_scenario = make_scenario(interventions=interventions)

    scenario.interventions.append("local change")
    assert other_scenario.interventions == ["not implemented"]
    assert interventions == ["not implemented"]


@pytest.mark.parametrize(
    ("name", "disease", "population", "duration", "error"),
    [
        (" ", make_disease(), make_population(), 1, ValueError),
        ("scenario", object(), make_population(), 1, TypeError),
        ("scenario", make_disease(), object(), 1, TypeError),
        ("scenario", make_disease(), make_population(), 0, ValueError),
        ("scenario", make_disease(), make_population(), float("inf"), ValueError),
        ("scenario", make_disease(), make_population(), "30", TypeError),
    ],
)
def test_scenario_rejects_invalid_values(
    name: str,
    disease: object,
    population: object,
    duration: object,
    error: type[Exception],
):
    with pytest.raises(error):
        Scenario(name, disease, population, duration)


def test_epidemiological_model_is_abstract():
    with pytest.raises(TypeError):
        EpidemiologicalModel()


def test_seir_model_can_be_instantiated_and_runs_simulation():
    results = SEIRModel().simulate(make_scenario())

    assert isinstance(results, SimulationResult)
    assert results.model_name == "SEIRModel"
    assert results.scenario_name == "Test scenario"
    assert results.days[0] == 0
    assert results.days[-1] == 30
    assert results.infected[0] == 10


def test_seir_conserves_population_and_returns_finite_nonnegative_values():
    total = 1000
    results = SEIRModel(beta=0.25).simulate(make_scenario())
    compartments = np.vstack(
        [
            results.susceptible,
            results.exposed,
            results.infected,
            results.recovered,
        ]
    )

    assert np.isfinite(compartments).all()
    assert compartments.min() >= -1e-8
    np.testing.assert_allclose(compartments.sum(axis=0), total, rtol=1e-8, atol=1e-7)


def test_population_without_exposed_or_infectious_has_no_transmission():
    results = SEIRModel().simulate(
        make_scenario(population=make_population(90, 0, 0, 10))
    )

    np.testing.assert_allclose(results.susceptible, 90)
    np.testing.assert_allclose(results.exposed, 0)
    np.testing.assert_allclose(results.infected, 0)
    np.testing.assert_allclose(results.recovered, 10)


def test_exposed_progress_to_infectious_without_new_transmission_when_beta_is_zero():
    results = SEIRModel(beta=0).simulate(
        make_scenario(population=make_population(90, 10, 0, 0))
    )

    assert results.exposed[1] < 10
    assert results.infected[1] > 0
    np.testing.assert_allclose(results.susceptible, 90)


def test_simulation_does_not_mutate_input_objects():
    disease = make_disease()
    population = make_population()
    scenario = Scenario("Original", disease, population, 30)
    original_disease = disease.__dict__.copy()
    original_population = population.__dict__.copy()
    original_interventions = scenario.interventions.copy()

    SEIRModel(beta=0.3).simulate(scenario)

    assert disease.__dict__ == original_disease
    assert population.__dict__ == original_population
    assert scenario.interventions == original_interventions


@pytest.mark.parametrize(
    ("beta", "error"),
    [
        (-0.1, ValueError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        ("0.2", TypeError),
    ],
)
def test_seir_rejects_invalid_beta(beta: object, error: type[Exception]):
    with pytest.raises(error):
        SEIRModel(beta=beta)


def test_seir_does_not_silently_ignore_interventions():
    with pytest.raises(NotImplementedError, match="does not apply interventions"):
        SEIRModel().simulate(make_scenario(interventions=["isolation"]))


def test_simulation_result_accepts_numpy_and_list_series():
    result = SimulationResult(
        days=[0, 1],
        susceptible=np.array([9.0, 8.0]),
        exposed=[1.0, 1.0],
        infected=[0.0, 1.0],
        recovered=[0.0, 0.0],
        model_name="SEIRModel",
        scenario_name="Example",
    )

    assert result.days.tolist() == [0.0, 1.0]
    assert result.model_name == "SEIRModel"
    assert result.scenario_name == "Example"


@pytest.mark.parametrize(
    "overrides",
    [
        {"exposed": [1.0]},
        {"infected": [float("nan"), 0.0]},
        {"recovered": [0.0, float("inf")]},
        {"days": [0.0, float("nan")]},
        {"days": [[0.0, 1.0]]},
        {"susceptible": [1.0, 2.0, 3.0]},
    ],
)
def test_simulation_result_rejects_invalid_series(overrides: dict[str, object]):
    values: dict[str, object] = {
        "days": [0.0, 1.0],
        "susceptible": [9.0, 8.0],
        "exposed": [1.0, 1.0],
        "infected": [0.0, 1.0],
        "recovered": [0.0, 0.0],
        "model_name": "SEIRModel",
        "scenario_name": "Example",
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        SimulationResult(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [("model_name", " "), ("scenario_name", "")],
)
def test_simulation_result_rejects_empty_metadata(field: str, value: str):
    values: dict[str, object] = {
        "days": [0.0],
        "susceptible": [1.0],
        "exposed": [0.0],
        "infected": [0.0],
        "recovered": [0.0],
        "model_name": "SEIRModel",
        "scenario_name": "Example",
    }
    values[field] = value

    with pytest.raises(ValueError):
        SimulationResult(**values)


def test_simulation_result_copies_input_and_exposes_read_only_series():
    susceptible = np.array([9.0, 8.0])
    result = SimulationResult(
        days=np.array([0.0, 1.0]),
        susceptible=susceptible,
        exposed=[1.0, 1.0],
        infected=[0.0, 1.0],
        recovered=[0.0, 0.0],
        model_name="SEIRModel",
        scenario_name="Example",
    )
    susceptible[0] = 100

    assert result.susceptible[0] == 9
    with pytest.raises(ValueError):
        result.susceptible[0] = 3
    with pytest.raises(ValueError):
        result.susceptible.setflags(write=True)
    with pytest.raises((AttributeError, TypeError)):
        result.model_name = "OtherModel"


def test_simulation_result_equality_compares_metadata_and_series_values():
    first = SimulationResult(
        days=[0.0],
        susceptible=[1.0],
        exposed=[0.0],
        infected=[0.0],
        recovered=[0.0],
        model_name="SEIRModel",
        scenario_name="Example",
    )
    same = SimulationResult(
        days=[0.0],
        susceptible=[1.0],
        exposed=[0.0],
        infected=[0.0],
        recovered=[0.0],
        model_name="SEIRModel",
        scenario_name="Example",
    )

    assert first == same