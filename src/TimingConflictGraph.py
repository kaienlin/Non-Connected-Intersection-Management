import itertools
import networkx as nx
import matplotlib.pyplot as plt

class TimingConflictGraph:
    def __init__(self, config):
        # construct vertex set
        self.V = set()
        for vehicle in config.vehicle_list:
            for zone in vehicle.trajectory:
                self.V.add((vehicle.id, zone))
        self.E = {vertex: set() for vertex in self.V}

        # Add Type-1 edges
        for vehicle in config.vehicle_list:
            for j, zone in enumerate(vehicle.trajectory[:-1]):
                self.E[(vehicle.id, zone)].add((vehicle.id, vehicle.trajectory[j+1], 1))
        
        # Add Type-2 edges
        for vehicle_list in config.lanes:
            for i, vehicle in enumerate(vehicle_list[:-1]):
                for follow in vehicle_list[i+1:]:
                    for zone in vehicle.trajectory:
                        self.try_add_edge((vehicle.id, zone), (follow.id, zone), 2)

        # Add Type-3 edges
        for lane1, lane2 in itertools.combinations(config.lanes, 2):
            for v1, v2 in itertools.product(lane1, lane2):
                for zone in v1.trajectory:
                    self.try_add_edge((v1.id, zone), (v2.id, zone), 3)
                    self.try_add_edge((v2.id, zone), (v1.id, zone), 3)

    def try_add_edge(self, src, dst, edge_type):
        if src in self.V and dst in self.V:
            self.E[src].add(dst + (edge_type, ))

    def remove_vehicles(self, removed_list):
        for v in list(self.V):
            if v[0] in removed_list:
                self.V.remove(v)
                self.E.pop(v)
                for u in self.V:
                    self.E[u].discard(v + (1,))
                    self.E[u].discard(v + (2,))
                    self.E[u].discard(v + (3,))

    def view(self, savepath=None):
        G = nx.DiGraph()
        for src, adj in self.E.items():
            for *dst, edge_type in adj:
                dst = tuple(dst)
                G.add_edge(str(src).strip('()'), str(dst).strip('()'), weight=edge_type)
        pos = nx.kamada_kawai_layout(G)
        type1 = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 1]
        type2 = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 2]
        type3 = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 3]
        nx.draw_networkx_edges(G, pos, node_size=800, edgelist=type1, width=1.5, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_edges(G, pos, node_size=800, edgelist=type2, edge_color='blue', width=1.5, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_edges(G, pos, node_size=800, edgelist=type3, edge_color='red', width=1.5, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_nodes(G, pos, node_size=800, edgecolors='black', node_color='white')
        nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")
        if savepath is not None:
            plt.savefig(savepath)
        else:
            plt.show()
        plt.clf()
