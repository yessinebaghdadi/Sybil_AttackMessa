import math

import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from mesa.experimental import JupyterViz, make_text
from Sybil.modelV1 import State, Sybil, number_Sybil, number_Normal



def agent_portrayal(graph):
    def get_agent(node):
        return graph.nodes[node]["agent"][0]

    edge_width = []
    edge_color = []
    for u, v in graph.edges():
        agent1 = get_agent(u)
        agent2 = get_agent(v)
        w = 2
        ec = "#e8e8e8"
        if State.SYBIL in (agent1.state, agent2.state):
            w = 3
            ec = "black"
        edge_width.append(w)
        edge_color.append(ec)
    
    # Adaptez les couleurs des nœuds pour les états Sybil et Normal
    node_color_dict = {
        State.SYBIL: "tab:red",
        State.NORMAL: "tab:blue",
    }
    node_color = [node_color_dict[get_agent(node).state] for node in graph.nodes()]
    
    return {
        "width": edge_width,
        "edge_color": edge_color,
        "node_color": node_color,
    }


def get_sybil_normal_ratio(model):
    # Met à jour le ratio pour afficher uniquement les états Sybil et Normal
    ratio = model.sybil_normal_ratio()
    ratio_text = r"$\infty$" if ratio is math.inf else f"{ratio:.2f}"
    sybil_text = str(number_Sybil(model))

    return f"Sybil/Normal Ratio: {ratio_text}<br>Sybil Nodes Remaining: {sybil_text}"


def make_plot(model):
    # Graphique pour les deux états Sybil et Normal uniquement
    fig = Figure()
    ax = fig.subplots()
    measures = ["Sybil", "Normal"]
    colors = ["tab:red", "tab:blue"]
    for i, m in enumerate(measures):
        color = colors[i]
        df = model.datacollector.get_model_vars_dataframe()
        ax.plot(df.loc[:, m], label=m, color=color)
    fig.legend()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig)


model_params = {
    "num_nodes": {
        "type": "SliderInt",
        "value": 10,
        "label": "Number of agents",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "avg_node_degree": {
        "type": "SliderInt",
        "value": 3,
        "label": "Avg Node Degree",
        "min": 3,
        "max": 8,
        "step": 1,
    },
    "sybil_infiltration_rate": {  # Paramètre pour simuler le taux d'infiltration Sybil
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Sybil Infiltration Rate",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
}

page = JupyterViz(
    Sybil,
    model_params,
    measures=[
        make_plot,
        make_text(get_sybil_normal_ratio),
    ],
    name="Sybil Model",
    agent_portrayal=agent_portrayal,
)
page  # noqa
