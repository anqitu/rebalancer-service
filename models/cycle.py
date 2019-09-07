from models.station_snapshot import StationSnapshot
from models.rebalance_schedule import RebalanceSchedule

class Cycle:

    def __init__(self, count, time, previous_cycle = None):
        self.count = count
        self.time = time
        self.rebalanced_bike_count = 0
        self.rebalance_cost = 0
        self.moved_bike_count = 0

        if previous_cycle:
            self.previous_cycle_lyapunov = previous_cycle.lyapunov
            self.cumulative_moved_bike_count = previous_cycle.cumulative_moved_bike_count
            self.cumulative_rebalanced_bike_count = previous_cycle.cumulative_rebalanced_bike_count
            self.cumulative_rebalance_cost = previous_cycle.cumulative_rebalance_cost
            self.cumulative_drift = previous_cycle.cumulative_drift
            self.time_avg_rebalance_cost = self.cumulative_rebalance_cost / self.count
        else:
            self.cumulative_moved_bike_count = 0
            self.cumulative_rebalanced_bike_count = 0
            self.cumulative_rebalance_cost = 0
            self.cumulative_drift = 0
            self.time_avg_rebalance_cost = 0

    def set_station_snapshots(self, station_snapshots):
        self.station_snapshots = station_snapshots

    def set_rebalance_schedules(self, rebalance_schedules):
        self.rebalance_schedules = rebalance_schedules
        self.rebalanced_bike_count = sum([rebalance_schedule.rebalanced_bike_count for rebalance_schedule in rebalance_schedules])
        self.rebalance_cost = sum([rebalance_schedule.rebalance_cost for rebalance_schedule in rebalance_schedules])
        self.cumulative_rebalanced_bike_count += self.rebalanced_bike_count
        self.cumulative_rebalance_cost += self.rebalance_cost

    def set_moved_bike_count(self):
        self.moved_bike_count = sum([station_snapshot.actual_incoming_bike_count for station_snapshot in self.station_snapshots])
        self.cumulative_moved_bike_count += self.moved_bike_count

    def set_lyapunov(self, lyapunov):
        self.lyapunov = lyapunov
        self.lyapunov_drift = 0 if (self.count == 0) else (self.lyapunov - self.previous_cycle_lyapunov)
        self.cumulative_drift += self.lyapunov_drift
        self.time_avg_cond_drift = 0 if (self.count == 0) else self.cumulative_drift / self.count
