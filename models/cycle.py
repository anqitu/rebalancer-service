from models.station_snapshot import StationSnapshot
from models.trip import Trip

class Cycle:

    def __init__(self, count, time, previous_cycle = None):
        self.count = count
        self.time = time
        self.rebalanced_bike_count = 0
        self.rebalance_cost = 0
        self.moved_bike_count = 0

        if previous_cycle:
            self.cumulative_moved_bike_count = previous_cycle.cumulative_moved_bike_count
            self.cumulative_rebalanced_bike_count = previous_cycle.cumulative_rebalanced_bike_count
            self.cumulative_rebalance_cost = previous_cycle.cumulative_rebalance_cost
        else:
            self.cumulative_moved_bike_count = 0
            self.cumulative_rebalanced_bike_count = 0
            self.cumulative_rebalance_cost = 0

    def set_station_snapshots(self, station_snapshots):
        self.station_snapshots = station_snapshots

    def set_trips(self, trips):
        self.trips = trips
        self.rebalanced_bike_count = sum([trip.rebalanced_bike_count for trip in trips])
        self.rebalance_cost = sum([trip.rebalance_cost for trip in trips])
        self.cumulative_rebalanced_bike_count += self.rebalanced_bike_count
        self.cumulative_rebalance_cost += self.rebalance_cost

    def set_moved_bike_count(self, moved_bike_count):
        self.moved_bike_count = moved_bike_count
        self.cumulative_moved_bike_count += moved_bike_count
