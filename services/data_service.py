import pandas as pd
import json

from models.station import Station

journeys_data_path = 'data/london_journeys_count_with_1h_interval.csv'
stations_data_path = 'data/london_stations.json'

class DataService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv(journeys_data_path)
        self.journeys_count_df['Time'] = pd.to_datetime(self.journeys_count_df['Time'],infer_datetime_format=True)

    def get_actual_flow_by_time(self, time):
        records = self.journeys_count_df[(self.journeys_count_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records.iterrows()}
        return records

    def get_station_data(self):
        with open(stations_data_path) as json_file:
            stations = json.load(json_file)
        return [Station(station['name'], station['id'], station['coordinates'], station['capacity']) for station in stations]

    def update_interval_hour(self, interval_hours):
        grouper = pd.Grouper(key='Time', freq=str(interval_hours*60) + 'Min', label='right')
        groups = self.journeys_count_df.groupby(['Station ID', grouper]).agg({'Out': 'sum', 'In': 'sum'})
        groups = groups.reset_index()
        groups['Time'] = groups['Time'] - pd.Timedelta(hours=interval_hours)
        self.journeys_count_df = groups
