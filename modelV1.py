from enum  import Enum
import math 
import mesa
import networkx as nx 

class State(Enum) : 
    NORMAL =0 
    SYBIL =1 

def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)

def number_Sybil(model):
    return number_state(model, State.SYBIL) 

def number_Normal(model):
    return number_state(model, State.NORMAL) 

def average_confidence_score(model): 
     normal_agents = [a.confidence_score for a in model.schedule.agents if a.state ==State.NORMAL]
     return sum(normal_agents)/len(normal_agents) if normal_agents else 0 

class Sybil(mesa.Model) : 
    def __init__(
            self, 
            num_nodes =10 , 
            avg_node_degree =3 , 
            initial_sybil_nodes =1 , 
            sybil_identity_count =3 , 
            normal_to_sybil_interaction_chance=0.3, 
            max_interactions_per_step=5     #ajouter  test
            ): 
               super().__init__() 
               self.num_nodes = num_nodes 
               prob = avg_node_degree /self.num_nodes  
               self.max_interactions_per_step = max_interactions_per_step #ajouter test
               self.G =nx.erdos_renyi_graph(n=self.num_nodes,p=prob)
               self.grid = mesa.space.NetworkGrid(self.G)
               self.initial_sybil_nodes = initial_sybil_nodes  
               self.schedule = mesa.time.RandomActivation(self)
               self.sybil_identity_count = sybil_identity_count 
               self.normal_to_sybil_interaction_chance = normal_to_sybil_interaction_chance 
               self.datacollector = mesa.DataCollector({
                    "Sybil": number_Sybil,
                    "Normal": number_Normal, 
                    "Average Confidence": average_confidence_score,
               }  ) 
               #creation agents 
               for i ,node in enumerate(self.G.nodes()): 
                   if i<self.initial_sybil_nodes: 
                          state =State.SYBIL  
                          confidence_score =0.2 
                   else: 
                          state = State.NORMAL  
                          confidence_score =1.0
                    
                   a = SybilAgent ( 
                          i,
                         self , 
                         state ,
                         self.sybil_identity_count , 
                         self.normal_to_sybil_interaction_chance , 
                         confidence_score
                    ) 
                   self.schedule.add(a) 

                   self.grid.place_agent(a, node)

                   self.running = True
                   self.datacollector.collect(self) 

    def step(self):
        self.schedule.step()
        # Collecte des données
        self.datacollector.collect(self)

class SybilAgent(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        sybil_identity_count,
        normal_to_sybil_interaction_chance, 
        confidence_score 
    ):
        super().__init__(unique_id, model)
        self.state = initial_state 
        self.confidence_score = confidence_score 
        self.sybil_identity_count = sybil_identity_count
        self.identities = [f"Sybil_{unique_id}_{i}" for i in range(sybil_identity_count)] if self.state == State.SYBIL else []
        self.normal_to_sybil_interaction_chance = normal_to_sybil_interaction_chance

    def interact_with_neighbors(self):
     neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
     interactions_count = 0  # Compteur pour limiter les interactions par étape

     for neighbor in neighbors:
        if interactions_count >= self.model.max_interactions_per_step:
            return  # Arrête la fonction dès que le nombre max d'interactions est atteint
        
        if self.state == State.SYBIL:
            # L'attaque se déclenche uniquement si le score de confiance est élevé
            if self.confidence_score >= 0.8:  # Abaisser le seuil
                if self.random.random() < self.normal_to_sybil_interaction_chance:
                    neighbor.influence_by_sybil()
                    interactions_count += 1   # Augmente le compteur d'interactions 
                    print(f"Sybil {self.unique_id} attaque {neighbor.unique_id}. Interactions: {interactions_count}")
            else:
                # Augmentation progressive de la confiance pour le nœud Sybil
                interaction_increase = 0.005 * (self.model.schedule.time / 10)
                self.confidence_score = min(1.0, self.confidence_score + interaction_increase)

        elif self.state == State.NORMAL:
            # Les nœuds normaux réduisent leur confiance en présence de voisins Sybil
            sybil_neighbors = [n for n in neighbors if n.state == State.SYBIL]
            if sybil_neighbors:
                self.confidence_score = max(0, self.confidence_score - 0.05)  # Augmenter la réduction
                if self.random.random() < self.normal_to_sybil_interaction_chance:
                    if self.random.random() < 0.1:
                        self.state = State.SYBIL
                        self.confidence_score = 0.1
                    interactions_count += 1  # Augmente le compteur d'interactions

    def influence_by_sybil(self):
     # Influence Sybil contrôlée par un seuil de confiance
     if self.state == State.NORMAL and self.confidence_score < 0.5:
        self.confidence_score += 0.1  # petit gain pour la progression
     elif self.confidence_score >= 1.0:
        self.state = State.SYBIL
        self.confidence_score = 0.2

   


    def step(self):
        self.interact_with_neighbors()
    
