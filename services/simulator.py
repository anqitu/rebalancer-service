import json

from models.cycle import Cycle
from models.setting import Setting
from models.simulation import Simulation
from models.station_snapshot import StationSnapshot
from models.station import Station
from models.trip import Trip

default_setting = Setting(2, 10, 5)

class Simulator:

    def __init__(self):
        self.simulation = Simulation(default_setting)
        self.stations = self.__get_stations_from_json()

        self.initialize_simulation()

    def initialize_simulation(self):
        self.cycle = Cycle(0, 0)
        self.simulation.add_cycle(self.cycle)
        self.station_snapshots = [StationSnapshot(station) for station in self.stations]
        self.cycle.set_station_snapshots(self.station_snapshots)
        self.__set_stations_data()

    def configure_setting(self, setting):
        self.simulation.set_setting(setting)

    def rebalance(self):
        self.__calculate_target_bike_count()
        self.__calculate_rebalanced_bike_count()
        self.__set_available_bike_count_after_rebalance()

        self.cycle.set_trips(self.__calculate_trips())
        self.cycle.set_moved_bike_count(self.__calculate_moved_bike_count())
        self.cycle.set_rebalanced_bike_count(self.__calculate_rebalanced_bike_count())
        self.cycle.set_rebalance_cost(self.__calculate_rebalance_cost())
        self.cycle.set_cumulative_moved_bike_count(self.__calculate_cumulative_moved_bike_count())
        self.cycle.set_cumulative_rebalanced_bike_count(self.__calculate_cumulative_rebalanced_bike_count())
        self.cycle.set_cumulative_rebalance_cost(self.__calculate_cumulative_rebalance_cost())

    def next_cycle(self):
        self.cycle = Cycle(self.cycle.count + 1, self.cycle.time + 2)
        self.simulation.add_cycle(self.cycle)
        self.station_snapshots = [StationSnapshot(station) for station in self.stations]
        self.cycle.set_station_snapshots(self.station_snapshots)
        self.__set_stations_data()

    def __get_stations_from_json(self):
        with open('data/london_stations.json') as json_file:
            stations = json.load(json_file)
        return [Station(station['name'], station['id'], station['coordinates'], station['bike_stands'],) for station in stations]

    def __set_stations_data(self):
        for station in self.station_snapshots:
            station.set_available_bike_count_before_rebalance(10)
            station.set_incoming_bike_count(10)
            station.set_outgoing_bike_count(10)

    def __calculate_target_bike_count(self):
        for station in self.station_snapshots:
            station.set_target_bike_count(10)

    def __calculate_rebalanced_bike_count(self):
        for station in self.station_snapshots:
            station.set_rebalanced_bike_count(10)

    def __set_available_bike_count_after_rebalance(self):
        for station in self.station_snapshots:
            station.set_available_bike_count_after_rebalance(20)

    def __calculate_trips(self):
        trips = [Trip(self.stations[0], self.stations[1])]
        [trip.set_rebalanced_bike_count(10) for trip in trips]
        return trips

    def __calculate_moved_bike_count(self):
        return 100

    def __calculate_rebalanced_bike_count(self):
        return 100

    def __calculate_rebalance_cost(self):
        return 100

    def __calculate_cumulative_moved_bike_count(self):
        return 100

    def __calculate_cumulative_rebalanced_bike_count(self):
        return 100

    def __calculate_cumulative_rebalance_cost(self):
        return 100
