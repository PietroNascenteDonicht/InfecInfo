import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from src.interface.dashboard import RESULT_KEY
from src.simulation.result import SimulationResult


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def open_simulator() -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    app.sidebar.radio[0].set_value("Simulador").run()
    return app


def decode_plotly_array(values: dict[str, str]) -> np.ndarray:
    return np.frombuffer(
        base64.b64decode(values["bdata"]),
        dtype=np.dtype(values["dtype"]),
    )


def test_dashboard_shows_empty_state_before_simulation():
    app = open_simulator()

    assert not app.exception
    assert any("Ainda não existem resultados" in item.value for item in app.info)
    assert not app.dataframe
    assert not app.get("plotly_chart")


def test_dashboard_displays_real_result_and_replaces_it_on_second_run():
    app = open_simulator()
    app.button[0].click().run()

    first_result = app.session_state[RESULT_KEY]
    assert isinstance(first_result, SimulationResult)
    assert not app.exception
    assert not app.error

    metrics = {item.label: item.value for item in app.metric}
    assert metrics["Suscetíveis (S)"] == f"{first_result.susceptible[-1]:,.2f}"
    assert metrics["Expostos (E)"] == f"{first_result.exposed[-1]:,.2f}"
    assert metrics["Infectados (I)"] == f"{first_result.infected[-1]:,.2f}"
    assert metrics["Recuperados (R)"] == f"{first_result.recovered[-1]:,.2f}"

    peak_index = int(np.argmax(first_result.infected))
    assert metrics["Pico de infectados"] == f"{first_result.infected[peak_index]:,.2f}"
    assert metrics["Dia do pico"] == f"{first_result.days[peak_index]:g}"
    assert metrics["Dias simulados"] == f"{first_result.days[-1]:g}"

    table = app.dataframe[0].value
    assert isinstance(table, pd.DataFrame)
    assert list(table.columns) == [
        "Dia",
        "Suscetíveis",
        "Expostos",
        "Infectados",
        "Recuperados",
    ]
    np.testing.assert_array_equal(table["Dia"].to_numpy(), first_result.days)
    np.testing.assert_array_equal(table["Suscetíveis"].to_numpy(), first_result.susceptible)
    np.testing.assert_array_equal(table["Expostos"].to_numpy(), first_result.exposed)
    np.testing.assert_array_equal(table["Infectados"].to_numpy(), first_result.infected)
    np.testing.assert_array_equal(table["Recuperados"].to_numpy(), first_result.recovered)

    chart_proto = app.get("plotly_chart")[0].proto
    chart_data = json.loads(chart_proto.spec)["data"]
    assert [trace["name"] for trace in chart_data] == [
        "Suscetíveis (S)",
        "Expostos (E)",
        "Infectados (I)",
        "Recuperados (R)",
    ]
    expected_series = (
        first_result.susceptible,
        first_result.exposed,
        first_result.infected,
        first_result.recovered,
    )
    for trace, expected in zip(chart_data, expected_series):
        np.testing.assert_array_equal(decode_plotly_array(trace["x"]), first_result.days)
        np.testing.assert_array_equal(decode_plotly_array(trace["y"]), expected)

    app.number_input(key="duration").set_value(10).run()
    app.number_input(key="beta").set_value(0.0).run()
    app.button[0].click().run()

    second_result = app.session_state[RESULT_KEY]
    assert isinstance(second_result, SimulationResult)
    assert second_result is not first_result
    assert second_result.days[-1] == 10
    assert app.metric[4].value == "10"
    assert len(app.dataframe) == 1
    assert app.dataframe[0].value["Dia"].iloc[-1] == 10
    updated_chart_data = json.loads(app.get("plotly_chart")[0].proto.spec)["data"]
    np.testing.assert_array_equal(
        decode_plotly_array(updated_chart_data[0]["x"]), second_result.days
    )
    for trace, expected in zip(
        updated_chart_data,
        (
            second_result.susceptible,
            second_result.exposed,
            second_result.infected,
            second_result.recovered,
        ),
    ):
        np.testing.assert_array_equal(decode_plotly_array(trace["y"]), expected)


def test_dashboard_reports_invalid_initial_population_without_stale_result():
    app = open_simulator()
    app.button[0].click().run()
    assert RESULT_KEY in app.session_state

    app.number_input(key="total_population").set_value(5).run()
    app.button[0].click().run()

    assert any("não pode exceder" in item.value for item in app.error)
    assert RESULT_KEY not in app.session_state
    assert not app.dataframe
    assert not app.get("plotly_chart")
    assert not app.info