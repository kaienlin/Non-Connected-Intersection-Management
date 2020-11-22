from TimingConflictGraph import TimingConflictGraph
import copy

class Scheduler:
    def __init__(self):
        pass

    def FCFS(self, config):
        conflict_graph = TimingConflictGraph(config)
        for src, adj in conflict_graph.G.items():
            to_remove = set()
            for *dst, edge_type in copy.copy(adj):
                dst = tuple(dst)
                if edge_type == 3 and config.vehicle_list[src[0]].arrival_time >= config.vehicle_list[dst[0]].arrival_time:
                    to_remove.add(dst + (edge_type, ))
            conflict_graph.G[src].difference_update(to_remove)
        conflict_graph.view()

    def run(self, config):
        self.FCFS(config)
