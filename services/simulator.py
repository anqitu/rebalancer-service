import json
import pandas as pd
from datetime import timedelta
import random
import math
from collections import OrderedDict

from models.cycle import Cycle
from models.settings import Settings
from models.simulation import Simulation
from models.station_snapshot import StationSnapshot
from models.station import Station
from models.rebalance_schedule import RebalanceSchedule
from models.result import Result
from services.data_service import DataService
from services.prediction_service import PredictionService
from utils import *
from constants import *

class Simulator:

    def __init__(self):
        self.data_service = DataService()

        self.setting = DEFAULT_SETTINGS
        self.time = START_TIME
        self.__update_status(STATUS_NONE)
        self.simulation = None
        self.cycle  = None

        self.stations = self.data_service.get_station_data()
        self.station_snapshots = {station.id: StationSnapshot(station = station) for station in self.stations}
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.set_initial_available_bike_count(0.7)

    def start_simulation(self):
        print_info('Start Simulation')
        self.simulation = Simulation(self.setting)
        # self.data_service.update_interval_hour(self.setting.interval_hour)
        self.prediction_service = PredictionService(self.setting)

        self.cycle = Cycle(0, START_TIME)
        self.simulation.add_cycle(self.cycle)
        self.cycle.set_station_snapshots(self.station_snapshots.values())
        self.__update_status(STATUS_START)

        self.__set_stations_data()
        self.cycle.set_supply_demand_gap_before_rebalance()

    def next_cycle(self):
        print_info('Start Next Cycle')
        self.cycle = Cycle(self.cycle.count + 1, self.time, self.cycle)
        self.simulation.add_cycle(self.cycle)
        self.station_snapshots = {station_snapshot.station.id: StationSnapshot(previous_station_snapshot = station_snapshot) for station_snapshot in self.station_snapshots.values()}
        self.cycle.set_station_snapshots(self.station_snapshots.values())
        self.__update_status(STATUS_NEXT_CYCLE)

        self.__set_stations_data()
        self.cycle.set_supply_demand_gap_before_rebalance()

    def rebalance(self):
        print_info('Start Rebalance')
        self.cycle.set_rebalance_schedules(self.__calculate_rebalance_schedules())
        self.__set_supply_demand_gap_after_rebalance()
        self.cycle.set_supply_demand_gap_after_rebalance()
        self.__update_status(STATUS_REBALANCE)

    def simulate_rides(self):
        print_info('Start Rides Simulation')
        self.__set_stations_available_available_bike_count_after_rides()
        self.cycle.set_moved_bike_count()
        self.__update_status(STATUS_RIDES)
        self.time = self.__next_cycle_time(self.cycle.time)

    def get_result(self):
        cycle = self.cycle
        setting = self.setting
        result = Result(time_avg_cost = cycle.time_avg_rebalance_cost,
                        time_avg_cond_drift = cycle.time_avg_cond_drift,
                        obj_function = cycle.time_avg_rebalance_cost * setting.cost_coef + cycle.time_avg_cond_drift,
                        moved_bike_total_count = cycle.cumulative_moved_bike_count,
                        rebalanced_bike_total_count = cycle.cumulative_rebalanced_bike_count,
                        cycle_count = cycle.count,
                        simulation_hour = (cycle.count+1) * setting.interval_hour,
                        distance_moved = cycle.distance_moved)
        self.simulation.set_result(result)
        return result

    def finish_simulation(self):
        self.__init__()
        self.__update_status(STATUS_FINISH)

    def __set_stations_data(self):
        print_info('Start setting stations data')
        actual_records = self.data_service.get_actual_flow_by_time(self.cycle.time)
        prediction_records = self.prediction_service.get_predict_flow_by_time(self.cycle.time)
        prediction_records_next_cycle = self.prediction_service.get_predict_flow_by_time(self.__next_cycle_time(self.cycle.time))

        for station_snapshot in self.station_snapshots.values():
            station_id = station_snapshot.station.id
            station_snapshot.set_actual_incoming_bike_count(actual_records[station_id]['in'])
            station_snapshot.set_actual_outgoing_bike_count(actual_records[station_id]['out'])

            station_snapshot.set_expected_incoming_bike_count(prediction_records[station_id]['in'])
            station_snapshot.set_expected_outgoing_bike_count(prediction_records[station_id]['out'])

            station_snapshot.set_next_cycle_expected_incoming_bike_count(prediction_records_next_cycle[station_id]['in'])
            station_snapshot.set_next_cycle_expected_outgoing_bike_count(prediction_records_next_cycle[station_id]['out'])

            station_snapshot.set_target_bike_count(self.__calculate_station_target_bike_count(station_snapshot))
            station_snapshot.set_next_cycle_target_bike_count(self.__calculate_station_next_cycle_target_bike_count(station_snapshot))
            station_snapshot.set_target_rebalance_bike_count(self.__calculate_target_rebalance_bike_count(station_snapshot))

        self.cycle.set_lyapunov(self.__calculate_lyapunov())

        print_info('Finish setting stations data')


    def __calculate_station_target_bike_count(self, station_snapshot):
        return min(station_snapshot.expected_outgoing_bike_count, station_snapshot.station.capacity)

    def __calculate_station_next_cycle_target_bike_count(self, station_snapshot):
        return min(station_snapshot.next_cycle_expected_outgoing_bike_count, station_snapshot.station.capacity)

    def __calculate_target_rebalance_bike_count(self, station_snapshot):
        setting = self.setting
        cost_per_bike = setting.peak_cost
        cost_coef = setting.cost_coef
        return max(math.floor(station_snapshot.next_cycle_target_bike_count \
               + station_snapshot.expected_outgoing_bike_count \
               - station_snapshot.available_bike_count_before_rebalance \
               - station_snapshot.expected_incoming_bike_count \
               - cost_coef * cost_per_bike), -1 * station_snapshot.available_bike_count_before_rebalance)

    def __set_supply_demand_gap_after_rebalance(self):
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.calculate_supply_demand_gap_after_rebalance()

    def __set_stations_available_available_bike_count_after_rides(self):
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.calculate_available_bike_count_after_rides()

    def __calculate_rebalance_schedules(self):
        print_info('Start calculating rebalance schedules for Cycle @{}'.format(self.time))
        destination_stations = {station_snapshot.station.id: {'station': station_snapshot.station,
                                 'rebalance_bike_count': station_snapshot.target_rebalance_bike_count} \
                                 for station_snapshot in self.station_snapshots.values() \
                                 if station_snapshot.target_rebalance_bike_count > 0}
        source_stations = {station_snapshot.station.id: {'station': station_snapshot.station,
                                 'rebalance_bike_count': station_snapshot.target_rebalance_bike_count} \
                                 for station_snapshot in self.station_snapshots.values() \
                                 if station_snapshot.target_rebalance_bike_count < 0}

        # print('-' * 40)
        # for key, value in destination_stations.items():
        #     print(key, ': ', value['rebalance_bike_count'])
        # print('-' * 40)
        # for key, value in source_stations.items():
        #     print(key, ': ', value['rebalance_bike_count'])

        destination_ids = sorted(list(destination_stations.keys()))
        source_ids = sorted(list(source_stations.keys()))

        setting = self.setting
        budget = setting.budget_per_cycle
        cost_per_bike = self.__get_current_cost_per_bike()

        rebalance_schedules = []
        for destination_id in destination_ids:
            source_distances = {source_id: calculate_distance_between_stations(destination_stations[destination_id]['station'],
                                                                               source_stations[source_id]['station']) \
                                                                               for source_id in source_ids}
            sorted_source_distances = dict(sorted(source_distances.items(), key=lambda kv: kv[1]))
            sorted_source_ids = list(sorted_source_distances.keys())

            # print('-' * 40)
            # print('destination_id: ', destination_id)
            # for key, value in sorted_source_distances.items():
            #     print(key, ': ', value)

            for source_id in sorted_source_ids:
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

                rebalance_cost = rebalanced_bike_count * cost_per_bike
                budget -= rebalance_cost
                rebalance_schedule = RebalanceSchedule(source_stations[source_id]['station'],
                                                     destination_stations[destination_id]['station'],
                                                     rebalanced_bike_count,
                                                     rebalance_cost)
                rebalance_schedules.append(rebalance_schedule)
                self.cycle.distance_moved += source_distances[source_id]
                # print(source_distances[source_id], self.cycle.distance_moved)

                self.station_snapshots[destination_id].update_rebalanced_bike_count(rebalanced_bike_count)
                self.station_snapshots[source_id].update_rebalanced_bike_count(rebalanced_bike_count * -1)

                # print(rebalance_schedule.__dict__)
                #
                # print('rebalance_bike_count: ', destination_stations[destination_id]['rebalance_bike_count'])
                # print('source_ids: ', source_ids)

                if destination_stations[destination_id]['rebalance_bike_count'] == 0 or math.floor(budget/cost_per_bike) == 0:
                    break

            if math.floor(budget/cost_per_bike) == 0:
                break

        print_info('Finish calculating rebalance schedules for Cycle @{}'.format(self.time))
        print_info('There are {} trips in total'.format(len(rebalance_schedules)))

        return rebalance_schedules

    def __calculate_lyapunov(self):
        return 0.5 * sum([(station_snapshot.available_bike_count_before_rebalance - station_snapshot.target_bike_count) ** 2 for station_snapshot in self.station_snapshots.values()])

    def __next_cycle_time(self, previous_time):
        return previous_time + timedelta(hours=self.setting.interval_hour)

    def __update_status(self, status):
        self.current_status = status
        self.__update_next_status()

    def __update_next_status(self):
        if self.current_status == None:
            self.next_status = STATUS_START
        elif self.current_status == STATUS_START:
            self.next_status = STATUS_REBALANCE
        elif self.current_status == STATUS_REBALANCE:
            self.next_status = STATUS_RIDES
        elif self.current_status == STATUS_RIDES:
            self.next_status = STATUS_NEXT_CYCLE
        elif self.current_status == STATUS_NEXT_CYCLE:
            self.next_status = STATUS_REBALANCE
        elif self.current_status == STATUS_FINISH:
            self.next_status = STATUS_START

    def __get_current_cost_per_bike(self):
        current_hour = self.time.hour
        if current_hour >=8 and current_hour <20:
            return self.setting.peak_cost
        else:
            return self.setting.off_peak_cost
