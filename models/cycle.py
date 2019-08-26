from models.station_snapshot import StationSnapshot
from models.trip import Trip

class Cycle:

    def __init__(self, count, time):
        self.count = count
        self.time = time

    def set_station_snapshots(self, station_snapshots):
        self.station_snapshots = station_snapshots

    def set_trips(self, trips):
        self.trips = trips

    def set_cumulative_moved_bike_count(self, cumulative_moved_bike_count):
        self.cumulative_moved_bike_count = cumulative_moved_bike_count

    def set_cumulative_rebalanced_bike_count(self, cumulative_rebalanced_bike_count):
        self.cumulative_rebalanced_bike_count = cumulative_rebalanced_bike_count

    def set_cumulative_rebalance_cost(self, cumulative_rebalance_cost):
        self.cumulative_rebalance_cost = cumulative_rebalance_cost
