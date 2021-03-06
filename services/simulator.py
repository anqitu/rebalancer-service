import json
import pandas as pd
from datetime import timedelta
from time import time
import random
import math
from collections import OrderedDict
from sklearn.metrics import mean_squared_error

from models.cycle import Cycle
from models.settings import Settings
from models.simulation import Simulation
from models.station_snapshot import StationSnapshot
from models.station import Station
from models.rebalance_schedule import RebalanceSchedule
from models.result import Result
from services.data_service import JourneyDataService, ResultDataService
from services.prediction_service import PredictionService
from utils import *
from constants import *

class Simulator:

    def __init__(self):
        self.journey_data_service = JourneyDataService()
        self.result_data_service = ResultDataService()

        self.settings = DEFAULT_SETTINGS
        self.stations = self.journey_data_service.get_station_data()
        self.__update_status(STATUS_NONE)

        self.__initialize()


    def __initialize(self):
        self.time = START_TIME
        self.simulation = None
        self.cycle = None
        self.station_snapshots = {station.id: StationSnapshot(station = station) for station in self.stations}
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.set_initial_available_bike_count(0.5)

    def start_simulation(self):
        print_info('Start Simulation')
        self.simulation_start_time = int(time())
        self.result_data_service.create_directory(self.simulation_start_time)

        self.simulation = Simulation(self.settings)
        self.prediction_service = PredictionService(self.settings)

        self.cycle = Cycle(0, START_TIME)
        self.simulation.add_cycle(self.cycle)
        self.cycle.set_station_snapshots(self.station_snapshots.values())
        self.__update_status(STATUS_START)

        self.__set_stations_data()

    def next_cycle(self):
        print()
        print_info('Start Next Cycle')
        self.cycle = Cycle(self.cycle.count + 1, self.time, self.cycle)
        self.simulation.add_cycle(self.cycle)
        self.station_snapshots = {station_snapshot.station.id: StationSnapshot(previous_station_snapshot = station_snapshot) for station_snapshot in self.station_snapshots.values()}
        self.cycle.set_station_snapshots(self.station_snapshots.values())
        self.__update_status(STATUS_NEXT_CYCLE)

        self.__set_stations_data()

    def rebalance(self):
        print_info('Start Rebalance')
        self.cycle.set_rebalance_schedules(self.__calculate_rebalance_schedules())
        self.__set_stations_demand_supply_gap()
        self.cycle.calculate_demand_supply_gap()
        self.__update_status(STATUS_REBALANCE)

    def simulate_rides(self):
        print_info('Start Rides Simulation')
        self.__set_stations_available_available_bike_count_after_rides()
        self.cycle.set_moved_bike_count()
        self.__update_status(STATUS_RIDES)
        self.time = self.__next_cycle_time(self.cycle.time)

        self.__record_cycle_results()
        self.__record_demand_supply_gap()

    def get_results(self):
        cycle = self.cycle
        settings = self.settings
        results = Result(time_avg_cost = round(cycle.time_avg_rebalance_cost, 3),
                        time_avg_cond_drift = round(cycle.time_avg_cond_drift, 3),
                        obj_function = round(cycle.time_avg_rebalance_cost * settings.cost_coef + cycle.time_avg_cond_drift, 3),
                        moved_bike_total_count = cycle.cumulative_moved_bike_count,
                        rebalanced_bike_total_count = cycle.cumulative_rebalanced_bike_count,
                        total_cycles = cycle.count + 1,
                        simulation_hour = (cycle.count+1) * settings.interval_hour,
                        distance_moved = cycle.distance_moved,
                        demand_supply_gap_total_decrement = cycle.cumulative_demand_supply_gap_decrement)
        self.simulation.set_result(results)
        return results

    def finish_simulation(self):
        self.__record_simulation_settings()
        self.__record_simulation_results()
        self.__update_status(STATUS_FINISH)
        self.__initialize()

    def get_all_simulation_records(self):
        return self.result_data_service.fetch_simulation_data()

    def __record_cycle_results(self):
        self.result_data_service.store_cycle_results(self.simulation_start_time, self.simulation.cycles[-1])

    def __record_demand_supply_gap(self):
        self.result_data_service.store_demand_supply_gap(self.cycle.station_snapshots, self.cycle.count)

    def __record_simulation_results(self):
        self.result_data_service.store_simulation_results(self.simulation_start_time, self.get_results())

    def __record_simulation_settings(self):
        self.result_data_service.store_simulation_settings(self.simulation_start_time, self.settings)

    def __set_stations_data(self):
        print_info('Start setting stations data')
        actual_records = self.journey_data_service.get_actual_flow_by_time(self.cycle.time)
        prediction_records = self.prediction_service.get_current_cycle_traffic_prediction_by_time(self.cycle.time)
        prediction_records_next_cycle = self.prediction_service.get_next_cycle_traffic_prediction_by_time(self.cycle.time)

        for station_snapshot in self.station_snapshots.values():
            station_id = station_snapshot.station.id
            station_snapshot.set_actual_incoming_bike_count(actual_records[station_id]['in'])
            station_snapshot.set_actual_outgoing_bike_count(actual_records[station_id]['out'])

            station_snapshot.set_expected_incoming_bike_count(prediction_records[station_id]['in'])
            station_snapshot.set_expected_outgoing_bike_count(prediction_records[station_id]['out'])

            station_snapshot.set_next_cycle_expected_incoming_bike_count(prediction_records_next_cycle[station_id]['in'])
            station_snapshot.set_next_cycle_expected_outgoing_bike_count(prediction_records_next_cycle[station_id]['out'])

            station_snapshot.set_target_bike_count(station_snapshot.expected_outgoing_bike_count)
            station_snapshot.set_next_cycle_target_bike_count(station_snapshot.next_cycle_expected_outgoing_bike_count)
            station_snapshot.set_target_rebalance_bike_count(self.__calculate_target_rebalance_bike_count(station_snapshot))

        # actual_incoming = [station_snapshot.actual_incoming_bike_count for station_snapshot in self.station_snapshots.values()]
        # expected_incoming = [station_snapshot.expected_incoming_bike_count for station_snapshot in self.station_snapshots.values()]
        # actual_outgoing = [station_snapshot.actual_outgoing_bike_count for station_snapshot in self.station_snapshots.values()]
        # expected_outgoing = [station_snapshot.expected_outgoing_bike_count for station_snapshot in self.station_snapshots.values()]
        # print_info('Incoming RMSE: {}'.format(round(mean_squared_error(actual_incoming, expected_incoming), 3)))
        # print_info('Outgoing RMSE: {}'.format(round(mean_squared_error(actual_outgoing, expected_outgoing), 3)))

        self.cycle.set_lyapunov(self.__calculate_lyapunov())

        print_info('Finish setting stations data')

    def __calculate_target_rebalance_bike_count(self, station_snapshot):
        settings = self.settings
        cost_per_bike = settings.peak_cost
        cost_coef = settings.cost_coef
        target_rebalance_bike_count = math.floor(min(station_snapshot.next_cycle_target_bike_count, station_snapshot.station.capacity) \
               + station_snapshot.expected_outgoing_bike_count \
               - station_snapshot.available_bike_count_before_rebalance \
               - station_snapshot.expected_incoming_bike_count \
               - cost_coef * cost_per_bike)

        return target_rebalance_bike_count

    def __set_stations_demand_supply_gap(self):
        for station_snapshot in self.station_snapshots.values():
            station_snapshot.calculate_demand_supply_gap()

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

        settings = self.settings
        budget = settings.budget_per_cycle
        cost_per_bike = self.__get_current_cost_per_bike()

        rebalance_schedules = []
        for destination_id in destination_ids:
            source_distances = {source_id: calculate_distance_between_stations(destination_stations[destination_id]['station'],
                                                                               source_stations[source_id]['station']) \
                                                                               for source_id in source_ids}
            # Sort source destinations based on distance to the current destination station
            sorted_source_distances = dict(sorted(source_distances.items(), key=lambda kv: kv[1]))
            sorted_source_ids = list(sorted_source_distances.keys())

            # print('-' * 40)
            # print('destination_id: ', destination_id)
            # for key, value in sorted_source_distances.items():
            #     print(key, ': ', value)

            for source_id in sorted_source_ids:
                destination_rebalance_bike_count = destination_stations[destination_id]['rebalance_bike_count']
                source_rebalance_bike_count = source_stations[source_id]['rebalance_bike_count']
                source_available_bike_count = self.station_snapshots[source_id].current_bike_count

                if abs(source_rebalance_bike_count) <= destination_rebalance_bike_count:
                    rebalanced_bike_count = min(abs(source_rebalance_bike_count), math.floor(budget/cost_per_bike), source_available_bike_count)
                else:
                    rebalanced_bike_count = min(destination_rebalance_bike_count, math.floor(budget/cost_per_bike), source_available_bike_count)

                if rebalanced_bike_count != 0:

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
        return previous_time + timedelta(hours=self.settings.interval_hour)

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
            return self.settings.peak_cost
        else:
            return self.settings.off_peak_cost
