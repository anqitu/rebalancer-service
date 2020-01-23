import pandas as pd
import numpy as np
import json

from constants import *
from models.station import Station
from sklearn.cluster import KMeans

class DataService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv(JOURNEYS_DATA_PATH, parse_dates=['Time'])

        self.stations = self.__load_station_data()
        # self.__calc_cluster_id()

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

    # def __calc_cluster_id(self):
    #     model = KMeans(n_clusters=CLUSTER_COUNT, random_state = 0)
    #     X = [station['coordinates'] for station in self.stations]
    #     model.fit(X)
    #     print(np.unique(model.labels_, return_counts=True))
    #
    #     for station, cluster in zip(self.stations, model.labels_):
    #         station['cluster_id'] = cluster


    def get_section_station_ids(self):

        return sections

    # """@TODO #remove later"""
    # def update_interval_hour(self, interval_hours):
    #     grouper = pd.Grouper(key='Time', freq=str(interval_hours*60) + 'Min', label='right')
    #     groups = self.journeys_count_df.groupby(['Station ID', grouper]).agg({'Out': 'sum', 'In': 'sum'})
    #     groups = groups.reset_index()
    #     groups['Time'] = groups['Time'] - pd.Timedelta(hours=interval_hours)
    #     self.journeys_count_df = groups



# with open('../data/london_stations.json') as json_file:
#     stations = json.load(json_file)
#
# CLUSTER_COUNT = 8
# from sklearn.cluster import KMeans
# model = KMeans(n_clusters=CLUSTER_COUNT)
# X = [station['coordinates'] for station in stations]
# model.fit(X)
# import numpy as np
# np.unique(model.labels_, return_counts=True)
# for station, cluster in zip(stations, model.labels_):
#     station['cluster_id'] = cluster
