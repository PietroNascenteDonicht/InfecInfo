import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.entities.disease import Disease
from src.entities.population import Population
from src.entities.scenario import Scenario
from src.models.seir import SEIRModel
from src.simulation.result import SimulationResult


RESULT_KEY = "simulation_result"


def render_simulation() -> None:
    """Render simulation inputs and the latest SEIR result."""
    st.header("Simulador SEIR")
    st.caption(
        "Valores pré-preenchidos são ilustrativos, não estimativas epidemiológicas."
    )
    failed = False

    with st.container():
        scenario_name = st.text_input(
            "Nome do cenário", "Cenário SEIR", key="scenario_name"
        )
        input_columns = st.columns(3)
        total_population = input_columns[0].number_input(
            "População total",
            min_value=1,
            value=1000,
            step=100,
            key="total_population",
        )
        initial_exposed = input_columns[1].number_input(
            "Expostos iniciais",
            min_value=0,
            value=0,
            step=1,
            key="initial_exposed",
        )
        initial_infected = input_columns[2].number_input(
            "Infectados iniciais",
            min_value=0,
            value=10,
            step=1,
            key="initial_infected",
        )

        state_columns = st.columns(3)
        initial_recovered = state_columns[0].number_input(
            "Recuperados iniciais",
            min_value=0,
            value=0,
            step=1,
            key="initial_recovered",
        )
        beta = state_columns[1].number_input(
            "Taxa efetiva de transmissão (beta)",
            min_value=0.0,
            value=0.25,
            step=0.05,
            format="%.4f",
            key="beta",
        )
        duration = state_columns[2].number_input(
            "Duração (dias)",
            min_value=1,
            max_value=3650,
            value=100,
            step=1,
            key="duration",
        )

        period_columns = st.columns(2)
        latent_period = period_columns[0].number_input(
            "Período latente (dias)",
            min_value=0.1,
            value=2.0,
            step=0.5,
            key="latent_period",
        )
        infectious_period = period_columns[1].number_input(
            "Período infeccioso (dias)",
            min_value=0.1,
            value=5.0,
            step=0.5,
            key="infectious_period",
        )
        submitted = st.button("Simular", type="primary")

    if submitted:
        st.session_state.pop(RESULT_KEY, None)
        occupied = initial_exposed + initial_infected + initial_recovered
        if occupied > total_population:
            failed = True
            st.error(
                "A soma dos expostos, infectados e recuperados iniciais "
                "não pode exceder a população total."
            )
        elif not scenario_name.strip():
            failed = True
            st.error("Informe um nome para o cenário.")
        else:
            susceptible = total_population - occupied
            try:
                with st.spinner("Executando a simulação SEIR..."):
                    disease = Disease(
                        name="Parâmetros definidos pelo usuário",
                        transmission_type="não especificado",
                        transmission_rate=beta,
                        symptomatic_rate=None,
                        asymptomatic_rate=None,
                        incubation_period=None,
                        infectious_period=infectious_period,
                        latent_period=latent_period,
                        severity=None,
                    )
                    population = Population(
                        total=total_population,
                        susceptible=susceptible,
                        exposed=initial_exposed,
                        infected=initial_infected,
                        recovered=initial_recovered,
                    )
                    scenario = Scenario(
                        name=scenario_name.strip(),
                        disease=disease,
                        population=population,
                        duration=duration,
                    )
                    result = SEIRModel(beta=beta).simulate(scenario)
                st.session_state[RESULT_KEY] = result
            except (TypeError, ValueError, RuntimeError, NotImplementedError) as error:
                failed = True
                st.error(f"Não foi possível concluir a simulação: {error}")
            except Exception as error:
                failed = True
                st.error(
                    "Ocorreu um erro inesperado durante a simulação. "
                    f"Detalhes: {error}"
                )

    result = st.session_state.get(RESULT_KEY)
    if not isinstance(result, SimulationResult):
        if not failed:
            st.info(
                "Ainda não existem resultados. Configure os parâmetros e clique em Simular."
            )
        return

    _render_results(result)


def _render_results(result: SimulationResult) -> None:
    final_values = (
        result.susceptible[-1],
        result.exposed[-1],
        result.infected[-1],
        result.recovered[-1],
    )
    peak_index = int(np.argmax(result.infected))

    st.subheader(f"Resultados: {result.scenario_name}")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Suscetíveis (S)", f"{final_values[0]:,.2f}")
    metric_columns[1].metric("Expostos (E)", f"{final_values[1]:,.2f}")
    metric_columns[2].metric("Infectados (I)", f"{final_values[2]:,.2f}")
    metric_columns[3].metric("Recuperados (R)", f"{final_values[3]:,.2f}")

    summary_columns = st.columns(3)
    summary_columns[0].metric("Dias simulados", f"{result.days[-1]:g}")
    summary_columns[1].metric("Pico de infectados", f"{result.infected[peak_index]:,.2f}")
    summary_columns[2].metric("Dia do pico", f"{result.days[peak_index]:g}")

    figure = go.Figure()
    series = (
        ("Suscetíveis (S)", result.susceptible, "#167D78"),
        ("Expostos (E)", result.exposed, "#D79B24"),
        ("Infectados (I)", result.infected, "#C54D4D"),
        ("Recuperados (R)", result.recovered, "#5367A5"),
    )
    for label, values, color in series:
        figure.add_trace(
            go.Scatter(
                x=result.days,
                y=values,
                mode="lines",
                name=label,
                line={"color": color, "width": 2},
                hovertemplate=f"Dia %{{x:.2f}}<br>{label}: %{{y:,.2f}}<extra></extra>",
            )
        )
    figure.update_layout(
        xaxis_title="Dias da simulação",
        yaxis_title="Quantidade de indivíduos",
        hovermode="x unified",
        legend_title="Compartimentos",
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    st.plotly_chart(figure, width="stretch", key="seir_results_chart")

    table = pd.DataFrame(
        {
            "Dia": result.days,
            "Suscetíveis": result.susceptible,
            "Expostos": result.exposed,
            "Infectados": result.infected,
            "Recuperados": result.recovered,
        }
    )
    st.dataframe(table, width="stretch", hide_index=True)