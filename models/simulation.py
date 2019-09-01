from models.setting import Setting
from models.cycle import Cycle

import time;

class Simulation:

    def __init__(self, setting):
        self.setting = setting
        self.start_time = time.time()
        self.cycles = []
        self.status = 'INIT'
        self.update_next_status()

    def set_setting(self, setting):
        self.setting = setting

    def set_result(self, result):
        self.result = result

    def add_cycle(self, cycle):
        self.cycles.append(cycle)

    def update_status(self, status):
        self.status = status
        self.update_next_status()

    def update_next_status(self):
        if self.status == 'INIT':
            self.next_status = 'START'
        elif self.status == 'START':
            self.next_status = 'REBALANCE'
        elif self.status == 'REBALANCE':
            self.next_status = 'RIDES'
        elif self.status == 'RIDES':
            self.next_status = 'NEXT CYCLE'
        elif self.status == 'NEXT CYCLE':
            self.next_status = 'REBALANCE'
        elif self.status == 'FINISH':
            self.next_status = None
