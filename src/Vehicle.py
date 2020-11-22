import copy

class Vehicle:
    def __init__(self, _id: int, connected: bool, arrival_time: int, trajectory: tuple):
        self.id = _id
        self.connected = connected
        self.arrival_time = arrival_time
        self.trajectory = trajectory
