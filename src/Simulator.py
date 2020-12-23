import sys

class Simulator:
    vertex_passing_time = 1
    edge_passing_time = 0
    def __init__(self, Gp, config):
        self.Gp = Gp
        self.config = config

    def _toposort(self, v, vis, topo):
        vis[v] = True
        for u in self.Gp.E[v]:
            dst = u[:2]
            edge_type = u[2]

            if not self.config.get_vehicle_by_id(dst[0]).connected:
                continue

            if not vis[dst] and edge_type != 1:
                self._toposort(dst, vis, topo)

        topo.insert(0, v)

    def toposort(self):
        topo = []
        vis = {v: False for v in self.Gp.V}
        for v in self.Gp.V:
            if not vis[v] and self.config.get_vehicle_by_id(v[0]).connected:
                self._toposort(v, vis, topo)
        return topo

    def simulate(self):
        vehicle_list = self.config.vehicle_list
        ready_time = [vehicle.arrival_time for vehicle in vehicle_list]
        position = ['start' for _ in vehicle_list]
        num_vehicles = len(position)
        available = {zone: True for vehicle in vehicle_list for zone in vehicle.trajectory}
        #topo = self.toposort()
        passing_order = {zone: [] for zone in available.keys()}
        for v in self.Gp.V:
            if self.config.get_vehicle_by_id(v[0]).connected:
                passing_order[v[1]].append(v[0])
        for zone in passing_order:
            passing_order[zone].sort(key=lambda vehicle_id: (self.config.get_vehicle_by_id(vehicle_id).arrival_time, self.config.get_vehicle_by_id(vehicle_id).id))

        available['end'] = True

        self.cur_time = 0
        def snapshot():
            print(f'\nt = {self.cur_time}')
            intersection_map = [[-1 for _ in range(4)] for _ in range(4)]
            zone_to_real_pos = {1: (1, 2), 2: (1, 1), 3: (2, 1), 4: (2, 2)}
            for idx, vehicle in enumerate(vehicle_list):
                print(vehicle.id, position[idx])
                if position[idx] != 'start' and position[idx] != 'end':
                    coord = zone_to_real_pos[position[idx]]
                    intersection_map[coord[0]][coord[1]] = vehicle.id

        snapshot()

        def next_zone(idx):
            if position[idx] == 'start':
                return vehicle_list[idx].trajectory[0]
            elif position[idx] == 'end':
                return 'end'
            elif vehicle_list[idx].trajectory.index(position[idx]) + 1 == len(vehicle_list[idx].trajectory):
                return 'end'
            else:
                return vehicle_list[idx].trajectory[vehicle_list[idx].trajectory.index(position[idx]) + 1]

        def proceed(idx, nxt):
            cur = position[idx]
            position[idx] = nxt
            #print(f'{vehicle_list[idx].id} move from {cur} to {nxt}')
            if ready_time[idx] < self.cur_time:
                ready_time[idx] = self.cur_time
            self.cur_time = ready_time[idx]
            ready_time[idx] += self.vertex_passing_time + self.edge_passing_time
            if cur != 'start':
                available[cur] = True
            if nxt != 'end':
                available[nxt] = False
            snapshot()
        
        while any(pos != 'end' for pos in position):
            is_live = False
            k = 0
            ready_time_order = sorted(list(range(num_vehicles)), key=lambda idx: ready_time[idx])
            while k < num_vehicles:
                vehicle_idx = ready_time_order[k]
                nxt = next_zone(vehicle_idx)
                if position[vehicle_idx] == 'end' or not available[nxt]:
                    k += 1
                    continue
                if vehicle_list[vehicle_idx].connected:
                    if nxt == 'end' or passing_order[nxt][0] == vehicle_list[vehicle_idx].id:
                        proceed(vehicle_idx, nxt)
                        is_live = True
                        if nxt != 'end':
                            passing_order[nxt].pop(0)
                        break
                else:
                    proceed(vehicle_idx, nxt)
                    is_live = True
                    break
                k += 1
            if not is_live:
                print('Deadlock!')
                sys.exit(0)
        
        print(f'Simulation completed. Total passing time = {self.cur_time:.6f}')

