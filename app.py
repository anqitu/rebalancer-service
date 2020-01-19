from flask import Flask, jsonify, request, send_file
from datetime import datetime
from flask_cors import CORS
import pandas as pd
from datetime import timedelta
import os
import zipfile
import io

from services.simulator import Simulator
from constants import *

app = Flask(__name__)
CORS(app)

simulator = Simulator()

settings_mapper = {'peak_cost': 'peakCost',
                    'off_peak_cost': 'offPeakCost',
                    'budget_per_cycle': 'budgetPerCycle',
                    'cost_coef': 'costCoef',
                    'prediction_mode': 'predictionMode'}

def get_stations():
    stations = []

    for station_snapshot in simulator.station_snapshots.values():
        station_response = {}
        station = station_snapshot.station
        station_response['name'] = station.name
        station_response['id'] = station.id
        station_response['coordinates'] = station.coordinates
        station_response['capacity'] = station.capacity
        station_response['count'] = station_snapshot.current_bike_count
        stations.append(station_response)

    return stations

def get_settings():
    settings = simulator.setting.__dict__
    settings_response = {}

    for setting, name in settings_mapper.items():
        settings_response[name] = settings[setting]
    return settings_response

def get_rebalance_schedules():
    rebalance_schedules = []

    for schedule in simulator.simulation.cycles[-1].rebalance_schedules:
        rebalance_schedule = {}
        rebalance_schedule['id'] = schedule.id
        rebalance_schedule['sourceId'] = schedule.source.id
        rebalance_schedule['destinationId'] = schedule.destination.id
        rebalance_schedule['count'] = schedule.rebalanced_bike_count
        rebalance_schedules.append(rebalance_schedule)

    return rebalance_schedules

def get_statistics():
    statistics = []

    current_cycle = simulator.simulation.cycles[-1]

    for attribute, name in {'count': 'Cycle Count',
                            'moved_bike_count': 'Moved Bikes',
                            'cumulative_moved_bike_count': 'Cumulative Moved Bikes',
                            'rebalanced_bike_count': 'Rebalanced Bikes',
                            'cumulative_rebalanced_bike_count': 'Cumulative Rebalanced Bikes',
                            'rebalance_cost': 'Rebalanced Cost',
                            'cumulative_rebalance_cost': 'Cumulative Rebalance Cost',
                            'time_avg_rebalance_cost': 'Time Average Rebalance Cost',
                            'trips': 'Trips',
                            'distance_moved': 'Distance Moved',
                            'cumulative_distance_moved': 'Cumulative Distance Moved',
                            'supply_demand_gap_before_rebalance': 'Supply Demand Gap Before Rebalance',
                            'supply_demand_gap_after_rebalance': 'Supply Demand Gap After Rebalance',
                            'lyapunov': 'Lyapunov',
                            'lyapunov_drift': 'Lyapunov Drift',
                            'cumulative_drift': 'Cumulative Lyapunov',
                            'time_avg_cond_drift': 'Time Average Conditional Drift'}.items():
        statistics.append({'name': name, 'value': getattr(current_cycle, attribute)})

    return statistics

def get_station_snapshots():
    station_snapshots = []

    for snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_snapshot = {}
        station = snapshot.station
        station_snapshot['id'] = station.id
        station_snapshot['count'] = snapshot.current_bike_count
        station_snapshots.append(station_snapshot)

    return station_snapshots

def get_status_response():
    response = {}
    response['time'] = datetime.timestamp(simulator.time)
    response['currentStatus'] = simulator.current_status
    response['nextStatus'] = simulator.next_status
    response['settings'] = get_settings()
    response['stations'] = get_stations()

    if simulator.simulation:
        response['statistics'] = get_statistics()

    return response

def get_step_response():
    response = {}

    response['time'] = datetime.timestamp(simulator.time)
    response['currentStatus'] = simulator.current_status
    response['nextStatus'] = simulator.next_status

    if response['currentStatus'] in [STATUS_START, STATUS_NEXT_CYCLE]:
        response['statistics'] = get_statistics()

    elif response['currentStatus'] == STATUS_REBALANCE:
        response['statistics'] = get_statistics()
        response['stations'] = get_station_snapshots()
        response['trips'] = get_rebalance_schedules()

    elif response['currentStatus'] == STATUS_RIDES:
        response['statistics'] = get_statistics()
        response['stations'] = get_station_snapshots()

    return response

def record_cycle_results():
    statistics = get_statistics()

    if simulator.cycle.count == 0:
        results = pd.DataFrame(columns = ['Time'] + [value['name'] for value in statistics])
    else:
        results = pd.read_csv(CYCLE_RESULTS_PATH)

    record = {value['name']:value['value'] for value in statistics}
    record['Time'] = simulator.time - timedelta(hours=simulator.setting.interval_hour)
    results = results.append(record, ignore_index=True )
    results.to_csv(CYCLE_RESULTS_PATH, index = False)

    station_snapshots = simulator.cycle.station_snapshots
    stations_ids = [station_snapshot.station.id for station_snapshot in station_snapshots]
    if simulator.cycle.count == 0:
        results = pd.DataFrame(data = {'Station ID': stations_ids})
    else:
        results = pd.read_csv(SUPPLY_DEMAND_GAP_PATH)
    results['Cycle{} (Bef)'.format(simulator.cycle.count)] = [station_snapshot.supply_demand_gap_before_rebalance for station_snapshot in station_snapshots]
    results['Cycle{} (Aft)'.format(simulator.cycle.count)] = [station_snapshot.supply_demand_gap_after_rebalance for station_snapshot in station_snapshots]
    results.to_csv(SUPPLY_DEMAND_GAP_PATH, index = False)


def get_result():
    response = []

    result = simulator.get_result()
    for attribute, name in {'cycle_count': 'Cycle Count',
                            'simulation_hour': 'Simulation Hours',
                            'moved_bike_total_count': 'Moved Bike Total Count',
                            'rebalanced_bike_total_count': 'Rebalanced Bike Total Count',
                            'time_avg_cost': 'Time Average Cost',
                            'time_avg_cond_drift': 'Time Average Conditional Drift',
                            'obj_function': 'Objective Function'}.items():
        response.append({'name': name, 'value': getattr(result, attribute)})


    settings = get_settings()
    settings_df = pd.DataFrame.from_dict(settings, orient='index')
    settings_df.to_csv(SETTING_PATH)

    result = {value['name']:value['value'] for value in response}
    result_df = pd.DataFrame.from_dict(result, orient='index')
    result_df.to_csv(SIMULATION_RESULT_PATH)

    return response

def get_finish_simulation_response(result):
    response = {}
    response['time'] = datetime.timestamp(simulator.time)
    response['currentStatus'] = simulator.current_status
    response['nextStatus'] = simulator.next_status
    response['statistics'] = result

    return response


@app.route("/status", methods = ['GET'])
def get_status():
    return jsonify(get_status_response())

@app.route("/config", methods = ['GET'])
def get_config():
    config = {
    'predictionMode': [PREDICTION_MODE_MOVING_AVG, PREDICTION_MODE_LSTM],
    }
    return jsonify(config)

@app.route("/step/{}".format(STATUS_START), methods = ['POST'])
def start_simulation():
    updated_settings = request.json['settings']
    for attribute, name in settings_mapper.items():
        setattr(simulator.setting, attribute, updated_settings[name])
    simulator.start_simulation()
    return jsonify(get_step_response())

@app.route("/step/{}".format(STATUS_NEXT_CYCLE), methods = ['POST'])
def next_cycle():
    simulator.next_cycle()
    return jsonify(get_step_response())

@app.route("/step/{}".format(STATUS_REBALANCE), methods = ['POST'])
def rebalance():
    simulator.rebalance()
    return jsonify(get_step_response())

@app.route("/step/{}".format(STATUS_RIDES), methods = ['POST'])
def simulate_rides():
    simulator.simulate_rides()
    record_cycle_results()
    return jsonify(get_step_response())

@app.route("/step/{}".format(STATUS_FINISH), methods = ['POST'])
def finish_simulation():
    result = get_result()
    simulator.finish_simulation()
    return jsonify(get_finish_simulation_response(result))

@app.route("/advance/<steps>".format(STATUS_FINISH), methods = ['POST'])
def advance_steps(steps):
    # Start simulation if settings in response
    if "settings" in request.json:
        updated_settings = request.json['settings']
        for attribute, name in settings_mapper.items():
            setattr(simulator.setting, attribute, updated_settings[name])
        simulator.start_simulation()

    for i in range(int(steps)):
        # Call next cycle if not a start
        if "settings" not in request.json:
            simulator.next_cycle()
        simulator.rebalance()
        simulator.simulate_rides()
        record_cycle_results()
    return jsonify(get_step_response())

@app.route("/download", methods = ['GET'])
def download_results():
    zipdir(RESULTS_PATH)
    return send_file(RESULTS_PATH + '.zip',
                        mimetype = 'application/zip',
                        attachment_filename= RESULTS_PATH + '.zip',
                        as_attachment = True)

def zipdir(path):
    zipf = zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()


if __name__ == "__main__":
    app.run(debug=True)
