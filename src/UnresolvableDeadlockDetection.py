import itertools

from Config import Config

class UnresolvableDeadlockDetection:
    def __init__(self, Gp, config):
        self.Gp = Gp
        self.config = config

    def add_not_sure_edge(self):
        for src, adj in self.Gp.E.items():
            src_connected = self.config.get_vehicle_by_id(src[0]).connected
            for *dst, edge_type in adj:
                dst = tuple(dst)
                dst_connected = self.config.get_vehicle_by_id(dst[0]).connected
                if edge_type == 3 and (not src_connected or not dst_connected):
                    self.Gp.try_add_edge(dst, src, 3)

    def add_wait_for_edges(self, v_i_j, v_ip_j, W):
        assert v_i_j[1] == v_ip_j[1]
        i = v_i_j[0]
        ip = v_ip_j[0]
        j = v_i_j[1]
        jpp_list = []
        for v_ip_jpp, adj in self.Gp.E.items():
            if v_ip_jpp[0] == ip and (ip, j, 1) in adj:
                jpp_list.append(v_ip_jpp[1])

        jp_list = [v[1] for v in self.Gp.E[v_i_j] if v[2] == 1]
        for jp, jpp in itertools.product(jp_list, jpp_list):
            W[(ip, jpp, j)].add((i, j, jp))

    def build_wait_for_graph(self):
        # wait-for graph
        W = dict()
        
        # construct vertex set
        for src, adj in self.Gp.E.items():
            for *dst, edge_type in adj:
                dst = tuple(dst)
                if edge_type == 1:
                    W[(src[0], src[1], dst[1])] = set()

        # construct edges
        for src, adj in self.Gp.E.items():
            for *dst, edge_type in adj:
                dst = tuple(dst)
                if edge_type == 2 or edge_type == 3:
                    self.add_wait_for_edges(src, dst, W)
        
        self.W = W

    def remove_vehicles_from_W(self, removed_list):
        for v in list(self.W.keys()):
            if v[0] in removed_list:
                del self.W[v]
            else:
                for u in list(self.W[v]):
                    if u[0] in removed_list:
                        self.W[v].remove(u)

    def dfs(self, v, p, color, count):
        color[v] = 'GREY'
        if p is None:
            count[v] = dict()
        else:
            count[v] = dict(count[p])
            if p[0] in count[v]:
                count[v][p[0]] += 1
            else:
                count[v][p[0]] = 1
        
        for u in list(self.W[v]):
            if color[u] == 'WHITE':
                self.dfs(u, v, color, count)
                if self.deadlock:
                    break
            elif color[u] == 'GREY':
                all_unique = True
                for vehicle, vehicle_cnt in count[v].items():
                    if vehicle_cnt - count[u].get(vehicle, vehicle_cnt) > 1:
                        all_unique = False
                        break
                if all_unique:
                    self.deadlock = True
                    new_config = self.config.split(u[0])
                    removed_vehicle_id = [vehicle.id for vehicle in new_config.vehicle_list]
                    self.removed_config.merge(new_config)
                    self.remove_vehicles_from_W(removed_vehicle_id)
                    self.Gp.remove_vehicles(removed_vehicle_id)
                    break
        color[v] = 'BLACK'

    def special_cycle_removal(self):
        self.removed_config = Config()
        self.removed_config.lanes = [[] for _ in range(len(self.config.lanes))]
        while True:
            self.deadlock = False
            color = {v: 'WHITE' for v in self.W.keys()}
            count = {v: None for v in self.W.keys()}
            for v in self.W:
                if color[v] == 'WHITE':
                    self.dfs(v, None, color, count)
                    if self.deadlock:
                        break
            if not self.deadlock:
                break

    def run(self):
        self.add_not_sure_edge()
        self.build_wait_for_graph()
        self.special_cycle_removal()
        return self.removed_config
