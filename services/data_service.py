import pandas as pd
import json

from constants import *
from models.station import Station

class DataService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv(JOURNEYS_DATA_PATH, parse_dates=['Time'])

    def get_actual_flow_by_time(self, time):
        records = self.journeys_count_df[(self.journeys_count_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records.iterrows()}
        return records

    def get_station_data(self):
        with open(STATIONS_DATA_PATH) as json_file:
            stations = json.load(json_file)
        return [Station(station['name'], station['id'], station['coordinates'], station['capacity']) for station in stations]

    """@TODO #remove later"""
    def update_interval_hour(self, interval_hours):
        grouper = pd.Grouper(key='Time', freq=str(interval_hours*60) + 'Min', label='right')
        groups = self.journeys_count_df.groupby(['Station ID', grouper]).agg({'Out': 'sum', 'In': 'sum'})
        groups = groups.reset_index()
        groups['Time'] = groups['Time'] - pd.Timedelta(hours=interval_hours)
        self.journeys_count_df = groups
