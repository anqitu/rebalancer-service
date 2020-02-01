import pandas as pd
import numpy as np
import json
import os

from constants import *
from models.station import Station
from sklearn.cluster import KMeans

class JourneyDataService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv(JOURNEYS_DATA_PATH, parse_dates=['Time'])
        self.stations = self.__load_station_data()

    def get_actual_flow_by_time(self, time):
        records = self.journeys_count_df[(self.journeys_count_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records.iterrows()}
        return records

    def __load_station_data(self):
        with open(STATIONS_DATA_PATH) as json_file:
            return json.load(json_file)

    def get_station_data(self):
        return [Station(station['name'], station['id'], station['coordinates'], station['capacity'])
            for station in self.stations]

class ResultDataService:
    def __init__(self):
        pass

    def create_directory(self, simulation_start_time):
        self.result_path = os.path.join(RESULTS_PATH, str(simulation_start_time))
        os.mkdir(self.result_path)

    def store_cycle_results(self, simulation_start_time, cycle_results):
        cycle_results_path = os.path.join(self.result_path, 'cycle_results.csv')

        cycle_results = cycle_results.__dict__

        if cycle_results['count'] == 0:
            results = pd.DataFrame(columns = ['Time'] + list(STATISTICS_MAPPER.values()))
        else:
            results = pd.read_csv(cycle_results_path)

        record = {name:cycle_results[result] for result, name in STATISTICS_MAPPER.items()}
        record['Time'] = cycle_results['time']
        results = results.append(record, ignore_index=True)
        results.to_csv(cycle_results_path, index = False)

        # station_snapshots = simulator.cycle.station_snapshots
        # stations_ids = [station_snapshot.station.id for station_snapshot in station_snapshots]
        # if simulator.cycle.count == 0:
        #     results = pd.DataFrame(data = {'Station ID': stations_ids})
        # else:
        #     results = pd.read_csv(supply_demand_gap_path)
        # results['Cycle{} (Bef)'.format(simulator.cycle.count)] = [station_snapshot.supply_demand_gap_before_rebalance for station_snapshot in station_snapshots]
        # results['Cycle{} (Aft)'.format(simulator.cycle.count)] = [station_snapshot.supply_demand_gap_after_rebalance for station_snapshot in station_snapshots]
        # results.to_csv(supply_demand_gap_path, index = False)

    def store_simulation_results(self, simulation_start_time, results):
        results = results.__dict__
        data = {}
        for result, name in RESULTS_MAPPER.items():
            data[name] = results[result]

        json_path = os.path.join(self.result_path, 'simulation_result.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        csv_path = os.path.join(self.result_path, 'simulation_result.csv')
        results_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        results_df.columns = ['result', 'value']
        results_df.to_csv(csv_path, index = False)

    def store_simulation_settings(self, simulation_start_time, settings):
        settings = settings.__dict__
        data = {}
        for setting, name in SETTINGS_CSV_MAPPER.items():
            data[name] = settings[setting]

        json_path = os.path.join(self.result_path, 'setting.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        csv_path = os.path.join(self.result_path, 'setting.csv')
        settings_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        settings_df.columns = ['setting', 'value']
        settings_df.to_csv(csv_path, index = False)
