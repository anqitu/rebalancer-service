from geopy.distance import distance
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt

def calculate_distance_between_stations(source, destination):
    return distance((source.coordinates[1],source.coordinates[0]),
                    (destination.coordinates[1], destination.coordinates[0])).km

def current_time():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def print_info(info):
    print("{:<6} {}: {}".format('[INFO]', current_time(), info))

def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_info('Make directory: {}'.format(directory))

def save_demand_supply_gap_plot(dir):

    results_df = pd.read_csv(os.path.join(dir, 'cycle_results.csv'), parse_dates=['Time'])
    results_df['Hour'] = results_df['Cycle Count'] * 2
    hours = results_df.shape[0] * 2

    fig = plt.figure(figsize=(12, 8))
    plt.title('Demand-Supply Gap', size=25, pad=20)
    plt.plot(results_df['Hour'], results_df['Demand Supply Gap Before Rebalance'], marker = 'o', markersize = 12)
    plt.plot(results_df['Hour'], results_df['Demand Supply Gap After Rebalance'], marker = 'v', markersize = 12)
    plt.xlabel('Hours in a Day', size=20)
    plt.ylabel('No. of Shareable Bikes', size=20)
    plt.xticks(size=15, ticks=range(0, hours, 2))
    plt.yticks(size=15)
    plt.legend(fontsize=14)
    fig.savefig(os.path.join(dir, 'Demand Supply Gap'), dpi = 200, bbox_inches = 'tight')
    plt.close()

def save_usage_vs_rebalance_plot(dir):
    results_df = pd.read_csv(os.path.join(dir, 'cycle_results.csv'), parse_dates=['Time'])
    results_df['Hour'] = results_df['Cycle Count'] * 2
    hours = results_df.shape[0] * 2

    fig = plt.figure(figsize=(12, 8))
    plt.title('Usage vs. Rebalance', size=25, pad=20)
    plt.plot(results_df['Hour'], results_df['Moved Bikes'], marker = 'o', markersize = 12)
    plt.plot(results_df['Hour'], results_df['Rebalanced Bikes'], marker = 'v', markersize = 12)
    plt.xlabel('Hours in a Day', size=20)
    plt.ylabel('No. of Shareable Bikes', size=20)
    plt.xticks(size=15, ticks=range(0, hours, 2))
    plt.yticks(size=15)
    plt.legend(fontsize=14)
    fig.savefig(os.path.join(dir, 'Usage vs Rebalance'), dpi = 200, bbox_inches = 'tight')
    plt.close()
