from Vehicle import Vehicle

class Config:
    def __init__(self, fname=None):
        if fname is None:
            self.lanes = [[], ]
            self.vehicle_list = tuple()
            return
            
        self.lanes = [[], ]
        with open(fname, 'r') as f:
            for line in f.readlines():
                line = [i.strip() for i in line.split()]
                if len(line) == 0:
                    self.lanes.append([])
                    continue
                connected = (line[0] == 'CONNECTED')
                arrival_time = int(line[1])
                trajectory = tuple(int(z) for z in line[2:])
                self.lanes[-1].append(Vehicle(-1, connected, arrival_time, trajectory))
        self.lanes = [x for x in self.lanes if x != []]
        self.vehicle_list = tuple([i for sublist in self.lanes for i in sublist])
        for i, vehicle in enumerate(self.vehicle_list):
            vehicle.id = i
        if not self.sanity_check():
            raise f'Error: Malformed Configuration: {fname}'

    def __str__(self):
        ret = ''
        for lane, vehicle_list in enumerate(self.lanes):
            ret += f'Lane {lane}: {len(vehicle_list)} vehicles\n'
            for vehicle in vehicle_list:
                ret += 'connected, ' if vehicle.connected else 'non-connected, '
                ret += f'arrival_time = {vehicle.arrival_time}, '
                ret += '<' + ', '.join([str(zone) for zone in vehicle.trajectory]) + '>\n'
            ret += '.\n'
        return ret

    def sanity_check(self):
        return True

    def get_vehicle_by_id(self, vehicle_id):
        for vehicle in self.vehicle_list:
            if vehicle.id == vehicle_id:
                return vehicle
        return None

    def split(self, vehicle_id):
        for lane, vehicle_list in enumerate(self.lanes):
            idx = None
            for i, vehicle in enumerate(vehicle_list):
                if vehicle_id == vehicle.id:
                    idx = i
                    break
            if idx is not None:
                new_config = Config()
                new_config.lanes = [[] for _ in range(len(self.lanes))]
                new_config.lanes[lane] = vehicle_list[idx:]
                new_config.vehicle_list = tuple([i for sublist in new_config.lanes for i in sublist])
                self.lanes[lane] = vehicle_list[:idx]
                self.vehicle_list = tuple([i for sublist in self.lanes for i in sublist])
                return new_config

        raise f"Error in Config.split({vehicle_id}): vehicle_id not in config"

    def merge(self, config):
        assert len(self.lanes) == len(config.lanes)

        for lane in range(len(self.lanes)):
            self.lanes[lane] = self.lanes[lane] + config.lanes[lane]
            self.lanes[lane].sort(key=lambda vehicle: vehicle.arrival_time)

        self.vehicle_list = tuple([i for sublist in self.lanes for i in sublist])
