import math
import mesa
from .modelV1 import State, Sybil, number_Sybil, number_Normal


def network_portrayal(G):
    # Le modèle garantit qu'il y a toujours un agent par nœud

    def node_color(agent):
        return {State.SYBIL: "#FF0000", State.NORMAL: "#008000"}.get(
            agent.state, "#808080"
        )

    def edge_color(agent1, agent2):
        # Les liens entre nœuds normaux et Sybil sont en gris
        if State.SYBIL in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        # Les liens avec des nœuds Sybil sont plus épais pour les différencier
        if State.SYBIL in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = {}
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}<br>confidence: {agents[0].confidence_score:.2f}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = mesa.visualization.NetworkModule(
    portrayal_method=network_portrayal,
    canvas_height=500,
    canvas_width=500,
)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Sybil", "Color": "#FF0000"},
        {"Label": "Normal", "Color": "#008000"},
    ]
)
confidence_chart = mesa.visualization.ChartModule(
    [
        {"Label": "Average Confidence", "Color": "#0000FF"},
    ]
)

def get_sybil_normal_ratio(model):
    total_normal = number_Normal(model)
    total_sybil = number_Sybil(model)
    ratio = total_sybil / total_normal if total_normal > 0 else math.inf
    ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"

    return f"Sybil/Normal Ratio: {ratio_text}<br>Sybil Nodes: {total_sybil}"



model_params = {
    "num_nodes": mesa.visualization.Slider(
        name="Nombre de nœuds",
        value=10,
        min_value=10,
        max_value=100,
        step=1,
        description="Choisir combien de nœuds inclure dans le modèle",
    ),
    "avg_node_degree": mesa.visualization.Slider(
        name="Degré moyen des nœuds",
        value=3,
        min_value=3,
        max_value=8,
        step=1,
        description="Degré moyen des nœuds",
    ),
    "initial_sybil_nodes": mesa.visualization.Slider(
        name="Nombre initial de nœuds Sybil",
        value=1,
        min_value=1,
        max_value=10,
        step=1,
        description="Nombre initial de nœuds Sybil dans le réseau",
    ),
    "sybil_identity_count": mesa.visualization.Slider(
        name="Nombre d'identités Sybil par nœud",
        value=3,
        min_value=1,
        max_value=10,
        step=1,
        description="Nombre d'identités Sybil qu'un nœud Sybil peut adopter",
    ),
    "normal_to_sybil_interaction_chance": mesa.visualization.Slider(
        name="Probabilité d'interaction normal-Sybil",
        value=0.3,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        description="Probabilité qu'un nœud normal devienne Sybil après interaction",
    ),
}

server = mesa.visualization.ModularServer(
    model_cls=Sybil,
    visualization_elements=[network, get_sybil_normal_ratio, chart,confidence_chart], #confidence_chart a mettre
    name="Sybil Attack on Network Model",
    model_params=model_params,
)
server.port = 8522  # Port du serveur pour le modèle Sybil Attack
