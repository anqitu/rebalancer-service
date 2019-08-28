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

    def set_result(self, result):
        self.result = result

    def add_cycle(self, cycle):
        self.cycles.append(cycle)
