from TimingConflictGraph import TimingConflictGraph
from UnresolvableDeadlock import remove_unresolvable_deadlock
import copy

class Scheduler:
    def __init__(self):
        pass

    def priority_cmp(self, u, v, config):
        # u < v
        u = config.get_vehicle_by_id(u)
        v = config.get_vehicle_by_id(v)
        return u.arrival_time > v.arrival_time or (u.arrival_time == v.arrival_time and u.id > v.id)

    def FCFS(self, config):
        conflict_graph = TimingConflictGraph(config)
        for src, adj in conflict_graph.E.items():
            to_remove = set()
            for *dst, edge_type in adj:
                dst = tuple(dst)
                if edge_type == 3 and self.priority_cmp(src[0], dst[0], config):
                    to_remove.add(dst + (edge_type, ))
            conflict_graph.E[src].difference_update(to_remove)
        return conflict_graph

    def run(self, config):
        Gp = self.FCFS(config)
        Gp.view('original.png')
        while True:
            removed_vehicle = remove_unresolvable_deadlock(Gp, config)
            config.remove(removed_vehicle)
            Gp = self.FCFS(config)
            if not removed_vehicle: break
            
        Gp.view('resolved.png')