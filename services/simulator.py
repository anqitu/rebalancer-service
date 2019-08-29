import json
import pandas as pd
import random
import math
from collections import OrderedDict

from models.cycle import Cycle
from models.setting import Setting
from models.simulation import Simulation
from models.station_snapshot import StationSnapshot
from models.station import Station
from models.rebalance_schedule import RebalanceSchedule
from models.result import Result
from services.data_service import DataService
from services.prediction_service import PredictionService
from utils import *

default_setting = Setting(interval_hour = 6, peak_cost = 10, off_peak_cost = 5, budget_per_cycle = 10000, cost_coef = 0.2)
first_cycle_start_time = pd.Timestamp(year = 2017, month = 8, day = 1, hour = 0)

class Simulator:

    def __init__(self):
        self.data_service = DataService()
        self.prediction_service = PredictionService()

        self.simulation = Simulation(default_setting)
        self.stations = self.data_service.get_station_data()
        self.station_snapshots = {station.id: StationSnapshot(station = station) for station in self.stations}
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.set_initial_available_bike_count(20)

    def configure_setting(self, setting):
        self.simulation.set_setting(setting)

    def start_simulation(self):
        self.cycle = Cycle(1, first_cycle_start_time)
        self.simulation.add_cycle(self.cycle)
        self.cycle.set_station_snapshots(self.station_snapshots.values())

        self.__set_stations_data()

    def next_cycle(self):
        self.cycle = Cycle(self.cycle.count + 1, self.__next_cycle_time(self.cycle.time), self.cycle)
        self.simulation.add_cycle(self.cycle)
        self.station_snapshots = {station_snapshot.station.id: StationSnapshot(previous_station_snapshot = station_snapshot) for station_snapshot in self.station_snapshots.values()}
        self.cycle.set_station_snapshots(self.station_snapshots.values())

        self.__set_stations_data()

    def rebalance(self):
        self.cycle.set_rebalance_schedules(self.__calculate_rebalance_schedules())

    def simulate_rides(self):
        self.__set_stations_available_available_bike_count_after_rides()
        self.cycle.set_moved_bike_count()

    def finish_simulation(self):
        cycle = self.cycle
        setting = self.simulation.setting
        self.simulation.set_result(Result(time_avg_cost = cycle.time_avg_rebalance_cost,
                                          time_avg_cond_drift = cycle.time_avg_cond_drift,
                                          obj_function = cycle.time_avg_rebalance_cost * setting.cost_coef + cycle.time_avg_cond_drift,
                                          moved_bike_total_count = cycle.cumulative_moved_bike_count,
                                          rebalanced_bike_total_count = cycle.cumulative_rebalanced_bike_count,
                                          cycle_count = cycle.count,
                                          simulation_hour = cycle.count * setting.interval_hour))


    def __set_stations_data(self):
        for station_snapshot in self.station_snapshots.values():

            station_data = self.data_service.get_journey_data(station_snapshot.station.id, self.cycle.time)
            station_snapshot.set_actual_incoming_bike_count(station_data['in'])
            station_snapshot.set_actual_outgoing_bike_count(station_data['out'])

            prediction_data = self.prediction_service.get_journey_data(station_snapshot.station.id, self.cycle.time)
            station_snapshot.set_expected_incoming_bike_count(station_data['in'] + random.randrange(-2, 3))
            station_snapshot.set_expected_outgoing_bike_count(station_data['out'] + random.randrange(-2, 3))

            next_cycle_station_data = self.prediction_service.get_journey_data(station_snapshot.station.id, self.__next_cycle_time(self.cycle.time))
            station_snapshot.set_next_cycle_expected_incoming_bike_count(station_data['in'] + random.randrange(-2, 3))
            station_snapshot.set_next_cycle_expected_outgoing_bike_count(station_data['out'] + random.randrange(-2, 3))

            station_snapshot.set_target_bike_count(self.__calculate_station_target_bike_count(station_snapshot))
            station_snapshot.set_next_cycle_target_bike_count(self.__calculate_station_next_cycle_target_bike_count(station_snapshot))
            station_snapshot.set_target_rebalance_bike_count(self.__calculate_target_rebalance_bike_count(station_snapshot))

        self.cycle.set_lyapunov(self.__calculate_lyapunov())


    def __calculate_station_target_bike_count(self, station_snapshot):
        return station_snapshot.available_bike_count_before_rebalance \
               + station_snapshot.expected_outgoing_bike_count \
               - station_snapshot.expected_incoming_bike_count

    def __calculate_station_next_cycle_target_bike_count(self, station_snapshot):
        return station_snapshot.available_bike_count_before_rebalance \
               + station_snapshot.expected_outgoing_bike_count \
               - station_snapshot.expected_incoming_bike_count \
               + station_snapshot.next_cycle_expected_outgoing_bike_count \
               - station_snapshot.next_cycle_expected_incoming_bike_count \

    def __calculate_target_rebalance_bike_count(self, station_snapshot):
        setting = self.simulation.setting
        cost_per_bike = setting.peak_cost
        cost_coef = setting.cost_coef
        return station_snapshot.next_cycle_target_bike_count \
               + station_snapshot.expected_outgoing_bike_count \
               - station_snapshot.available_bike_count_before_rebalance \
               - station_snapshot.expected_incoming_bike_count \
               - cost_coef * cost_per_bike

    def __set_stations_available_available_bike_count_after_rides(self):
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.calculate_available_bike_count_after_rides()

    def __calculate_rebalance_schedules(self):
        destination_stations = {station_snapshot.station.id: {'station': station_snapshot.station,
                                 'rebalance_bike_count': station_snapshot.target_rebalance_bike_count} \
                                 for station_snapshot in self.station_snapshots.values() \
                                 if station_snapshot.target_rebalance_bike_count > 0}
        source_stations = {station_snapshot.station.id: {'station': station_snapshot.station,
                                 'rebalance_bike_count': station_snapshot.target_rebalance_bike_count} \
                                 for station_snapshot in self.station_snapshots.values() \
                                 if station_snapshot.target_rebalance_bike_count < 0}

        print('-' * 40)
        for key, value in destination_stations.items():
            print(key, ': ', value['rebalance_bike_count'])
        print('-' * 40)
        for key, value in source_stations.items():
            print(key, ': ', value['rebalance_bike_count'])

        destination_ids = sorted(list(destination_stations.keys()))
        source_ids = sorted(list(source_stations.keys()))

        setting = self.simulation.setting
        budget = setting.budget_per_cycle
        cost_per_bike = setting.peak_cost

        rebalance_schedules = []
        for destination_id in destination_ids:
            source_distances = {source_id: calculate_distance_between_stations(destination_stations[destination_id]['station'],
                                                                               source_stations[source_id]['station']) \
                                                                               for source_id in source_ids}
            sorted_source_distances = dict(sorted(source_distances.items(), key=lambda kv: kv[1]))
            sorted_source_ids = list(sorted_source_distances.keys())

            print('-' * 40)
            print('destination_id: ', destination_id)
            for key, value in sorted_source_distances.items():
                print(key, ': ', value)

            while destination_stations[destination_id]['rebalance_bike_count'] > 0 and len(source_ids) != 0:
                source_id = sorted_source_ids[0]

                destination_rebalance_bike_count = destination_stations[destination_id]['rebalance_bike_count']
                source_rebalance_bike_count = source_stations[source_id]['rebalance_bike_count']
                if abs(source_rebalance_bike_count) <= destination_rebalance_bike_count:
                    rebalanced_bike_count = min(abs(source_rebalance_bike_count), math.floor(budget/cost_per_bike))
                else:
                    rebalanced_bike_count = min(destination_rebalance_bike_count, math.floor(budget/cost_per_bike))

                destination_stations[destination_id]['rebalance_bike_count'] = destination_rebalance_bike_count - rebalanced_bike_count
                source_stations[source_id]['rebalance_bike_count'] = source_rebalance_bike_count + rebalanced_bike_count

                if source_stations[source_id]['rebalance_bike_count'] == 0:
                    source_ids.remove(source_id)
                    del sorted_source_ids[0]

                rebalance_cost = rebalanced_bike_count * cost_per_bike
                budget -= rebalance_cost
                rebalance_schedule = RebalanceSchedule(source_stations[source_id]['station'],
                                                     destination_stations[destination_id]['station'],
                                                     rebalanced_bike_count,
                                                     rebalance_cost)
                rebalance_schedules.append(rebalance_schedule)

                self.station_snapshots[destination_id].change_rebalanced_bike_count(rebalanced_bike_count)
                self.station_snapshots[source_id].change_rebalanced_bike_count(rebalanced_bike_count * -1)

                print(rebalance_schedule.__dict__)

        return rebalance_schedules

    def __calculate_lyapunov(self):
        return 0.5 * sum([(station_snapshot.available_bike_count_before_rebalance - station_snapshot.target_bike_count) ** 2 for station_snapshot in self.station_snapshots.values()])

    def __next_cycle_time(self, previous_time):
        return previous_time + pd.Timedelta(hours=self.simulation.setting.interval_hour)
