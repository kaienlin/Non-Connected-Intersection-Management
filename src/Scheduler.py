from TimingConflictGraph import TimingConflictGraph
from UnresolvableDeadlockDetection import UnresolvableDeadlockDetection
from Config import Config
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

    def add_not_sure_edge(self, config, G):
        for src, adj in G.E.items():
            src_connected = config.get_vehicle_by_id(src[0]).connected
            for *dst, edge_type in adj:
                dst = tuple(dst)
                if edge_type == 3 and (not src_connected or not config.get_vehicle_by_id(dst[0]).connected):
                    G.try_add_edge(dst, src, 3)

    def run(self, config):
        schedule_list = []
        rest_config = copy.deepcopy(config)
        while True:
            Gp = self.FCFS(rest_config)
            deadlock_detection = UnresolvableDeadlockDetection(Gp, rest_config)
            removed_config = deadlock_detection.run()
            schedule_list.append(Gp)
            if not removed_config.vehicle_list:
                break
            rest_config = removed_config

        return schedule_list
