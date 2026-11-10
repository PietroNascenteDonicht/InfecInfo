# EpiSim — Simulador Epidemiológico In Silico

> Projeto de modelagem e simulação computacional da disseminação de doenças infecciosas.

## 1. Sobre o projeto

O **EpiSim** é um projeto de pesquisa e desenvolvimento computacional que busca investigar como diferentes agentes infecciosos se disseminam em populações e como fatores ambientais, sociais e comportamentais influenciam a propagação de doenças.

Por meio de modelos matemáticos e simulações computacionais, o projeto pretende reproduzir cenários epidemiológicos fictícios e analisar os efeitos de diferentes estratégias de prevenção e controle.

O desenvolvimento será realizado na abordagem *in silico*, utilizando ferramentas computacionais para testar hipóteses sem a necessidade de experimentos biológicos em seres humanos ou animais.

## 2. Objetivo geral

Desenvolver um simulador epidemiológico capaz de representar a disseminação de doenças infecciosas e avaliar como diferentes fatores influenciam sua propagação em uma população.

### Objetivos específicos

- Compreender os mecanismos de transmissão de diferentes agentes infecciosos.
- Implementar modelos matemáticos de disseminação epidemiológica.
- Simular a propagação de doenças em populações virtuais.
- Avaliar a influência da mobilidade populacional na transmissão.
- Investigar o impacto de medidas preventivas.
- Comparar diferentes cenários epidemiológicos.
- Interpretar os resultados por meio de indicadores e visualizações gráficas.

## 3. Doenças utilizadas como referência

O projeto utilizará doenças infecciosas reais como referência para compreender diferentes mecanismos de transmissão.

| Doença | Agente infeccioso | Transmissão predominante |
|---|---|---|
| COVID-19 | SARS-CoV-2 | Respiratória |
| Ebola | Ebolavirus | Contato direto com fluidos corporais infectados |
| Hantavirose | Hantavírus | Exposição a roedores infectados e suas excreções |
| Varíola | Variola virus | Respiratória e contato direto |

As doenças serão utilizadas como referências epidemiológicas. As simulações não representam necessariamente a reprodução exata de epidemias históricas.

## 4. Fundamentação matemática

O projeto utilizará modelos compartimentais de epidemiologia.

### Modelo SEIR

O modelo SEIR divide a população em quatro categorias:

- **S — Suscetíveis:** indivíduos que podem contrair a infecção.
- **E — Expostos:** indivíduos infectados que ainda não são infecciosos. O período latente não é necessariamente igual ao período de incubação.
- **I — Infectados:** indivíduos capazes de transmitir a doença.
- **R — Recuperados/Removidos:** indivíduos que deixaram o grupo de infectados.

O SEIR implementado resolve as equações diferenciais:

```text
dS/dt = -beta * S * I / N
dE/dt =  beta * S * I / N - sigma * E
dI/dt =  sigma * E - gamma * I
dR/dt =  gamma * I
```

com `sigma = 1 / período latente`, `gamma = 1 / período infeccioso` e `N = S + E + I + R`. O modelo pressupõe população fechada, mistura homogênea e taxas constantes. `beta` pode ser configurado no `SEIRModel`; se omitido, usa `Disease.transmission_rate`.

Modelos adicionais poderão ser implementados conforme as características epidemiológicas de cada doença.

## 5. Variáveis da simulação

### Variáveis populacionais
- População total.
- Número inicial de infectados.
- Distribuição populacional.
- Frequência de contatos.
- Mobilidade entre regiões.

### Variáveis epidemiológicas
- Taxa de transmissão.
- Período de incubação.
- Período de transmissibilidade.
- Taxa de recuperação.
- Suscetibilidade da população.

### Variáveis de intervenção
- Cobertura vacinal.
- Redução de contatos.
- Isolamento de infectados.
- Medidas de proteção.
- Redução da mobilidade.

Os parâmetros deverão ser documentados e fundamentados em fontes epidemiológicas confiáveis quando forem utilizados dados de doenças reais.

## 6. Experimentos computacionais

O EpiSim permitirá executar diferentes experimentos para investigar hipóteses.

### Experimento 1 — Disseminação sem intervenção

Simular uma população sem medidas preventivas e observar a evolução da infecção.

### Experimento 2 — Redução da mobilidade

Investigar como a diminuição do deslocamento entre regiões influencia a disseminação.

### Experimento 3 — Vacinação

Avaliar como diferentes níveis de cobertura vacinal alteram a dinâmica epidemiológica, considerando as características da vacina e da doença.

### Experimento 4 — Isolamento

Investigar como a identificação e o isolamento de indivíduos infectados influenciam a transmissão.

### Experimento 5 — Comparação entre doenças

Comparar doenças com diferentes mecanismos de transmissão e analisar como suas características alteram os resultados das simulações.

## 7. Indicadores e resultados

O simulador deverá apresentar:

- Total de indivíduos suscetíveis.
- Total de indivíduos expostos.
- Total de indivíduos infectados.
- Total de indivíduos recuperados ou removidos.
- Pico de infecção.
- Dia de ocorrência do pico.
- Incidência ao longo do tempo.
- Comparação entre cenários.

Os resultados serão apresentados por meio de gráficos e tabelas.

## 8. Tecnologias previstas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do simulador |
| NumPy | Operações matemáticas |
| SciPy | Modelagem e resolução numérica |
| pytest | Testes automatizados |
| Streamlit | Interface interativa |

## Executar e testar

Instale as dependências e execute os testes na raiz do projeto:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Para iniciar a interface Streamlit:

```bash
streamlit run app.py
```

Na página **Simulador**, configure a população inicial, a taxa de transmissão, os períodos latente e infeccioso e a duração. Depois de clicar em **Simular**, a tela apresenta os compartimentos no último dia, pico de infectados, série temporal Plotly e tabela diária. A simulação utiliza somente parâmetros informados; metadados epidemiológicos não usados pelo modelo ficam sem especificação.

Exemplo de execução. Os parâmetros abaixo são sintéticos e servem somente para demonstrar a API, não representam estimativas epidemiológicas:

```python
from src.entities.disease import Disease
from src.entities.population import Population
from src.entities.scenario import Scenario
from src.models.seir import SEIRModel

disease = Disease(
	name="Synthetic example",
	transmission_type="unspecified",
	transmission_rate=0.25,
	symptomatic_rate=0.5,
	asymptomatic_rate=0.5,
	incubation_period=4.0,
	infectious_period=5.0,
	latent_period=2.0,
	severity=0.1,
)
population = Population(1000, 990, 0, 10, 0)
scenario = Scenario("Demo", disease, population, duration=30)
results = SEIRModel(beta=0.25).simulate(scenario)
print(results.days[-1])
print(results.susceptible[0], results.infected[0])
```

Saída esperada: `30.0` e `990.0 10.0`. As séries são arrays NumPy acessíveis pelos atributos `days`, `susceptible`, `exposed`, `infected` e `recovered`, e podem ser passadas diretamente ao Pandas ou Plotly.

## 9. Estrutura atual do projeto

```text
EpiSim/
├── src/
│   ├── entities/
│   │   ├── disease.py
│   │   ├── population.py
│   │   └── scenario.py
│   ├── models/
│   │   ├── base.py
│   │   └── seir.py
│   ├── simulation/
│   ├── analysis/
│   └── interface/
│       └── dashboard.py
├── app.py
├── tests/
│   └── test_episim.py
├── requirements.txt
└── readme.md
```

## 10. Metodologia de desenvolvimento

O desenvolvimento será dividido em etapas:

1. **Pesquisa bibliográfica:** levantamento de informações sobre agentes infecciosos, transmissão e epidemiologia.
2. **Definição dos modelos:** escolha e documentação dos modelos matemáticos.
3. **Implementação:** desenvolvimento dos modelos computacionais em Python.
4. **Validação:** verificação das equações, parâmetros, comportamento esperado e consistência dos resultados.
5. **Experimentação:** execução de simulações com diferentes condições.
6. **Análise:** interpretação dos resultados e comparação entre cenários.
7. **Documentação:** elaboração dos relatórios científicos e apresentação dos resultados.

## 11. Limitações científicas

O EpiSim é uma ferramenta de simulação e investigação, não um sistema de diagnóstico ou previsão clínica.

Os resultados dependem das hipóteses, parâmetros e simplificações utilizadas nos modelos.

Cada doença possui características epidemiológicas próprias. Portanto, um único modelo não representa adequadamente todos os mecanismos de transmissão.

As simulações devem ser interpretadas como experimentos computacionais, e não como previsões exatas de epidemias reais. O SEIR básico não inclui estrutura etária, contatos heterogêneos, reinfecção, mortalidade, sazonalidade nem intervenções; cenários com intervenções são rejeitados pelo modelo atual. CFR (letalidade entre casos) e IFR (letalidade entre todas as infecções) são campos opcionais distintos e não participam das equações.

## 12. Resultados esperados

Espera-se desenvolver uma ferramenta capaz de demonstrar matematicamente como doenças infecciosas podem se disseminar e como diferentes intervenções podem modificar sua dinâmica.

O projeto também pretende contribuir para a compreensão da importância da vigilância epidemiológica, da prevenção e da cooperação internacional no controle de doenças infecciosas.

---

**EpiSim — Modelando a disseminação. Investigando a prevenção.**