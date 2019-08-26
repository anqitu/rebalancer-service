from models.setting import Setting
from models.cycle import Cycle

import time;

class Simulation:

    def __init__(self, setting):
        self.setting = setting
        self.start_time = time.time()
        self.cycles = []

    def set_setting(self, setting):
        self.setting = setting

    def set_total_cost(self, total_cost):
        self.total_cost = total_cost

    def set_drift(self, drift):
        self.drift = drift

    def set_moved_bike_total_count(self, moved_bike_total_count):
        self.moved_bike_total_count = moved_bike_total_count

    def set_rebalanced_bike_total_count(self, rebalanced_bike_total_count):
        self.rebalanced_bike_total_count = rebalanced_bike_total_count

    def add_cycle(self, cycle):
        self.cycles.append(cycle)
