from flask import Flask, jsonify, request, send_file
from datetime import datetime
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from datetime import timedelta
import os
import zipfile
import io
import shutil

from services.simulator import Simulator
from constants import *

app = Flask(__name__)
CORS(app)

simulator = Simulator()

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
    settings = simulator.settings.__dict__
    settings_response = {}

    for setting, name in SETTINGS_UI_MAPPER.items():
        settings_response[name] = settings[setting]
    return settings_response

def get_rebalance_schedules():
    rebalance_schedules = simulator.simulation.cycles[-1].rebalance_schedules
    if len(rebalance_schedules) == 0:
        return []

    if 6 <= len(rebalance_schedules) <= 10:
        n_clusters = 2
    else:
        n_clusters = (len(rebalance_schedules) - 1) // 10 + 1

    model = KMeans(n_clusters=n_clusters, random_state = 0)
    X = [schedule.source.coordinates for schedule in rebalance_schedules]
    model.fit(X)
    print(np.unique(model.labels_, return_counts=True))

    schedules_response = [[] for i in range(n_clusters)]
    for schedule, cluster in zip(rebalance_schedules, model.labels_):
        schedule_response = {}
        schedule_response['id'] = schedule.id
        schedule_response['sourceId'] = schedule.source.id
        schedule_response['destinationId'] = schedule.destination.id
        schedule_response['count'] = schedule.rebalanced_bike_count
        schedules_response[cluster].append(schedule_response)

    schedules_response = [schedule for schedule in schedules_response if len(schedule) > 0]

    return schedules_response

def get_statistics():
    statistics = []

    current_cycle = simulator.simulation.cycles[-1]

    for attribute, name in STATISTICS_MAPPER.items():
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

def get_results():
    response = []

    results = simulator.get_results()
    for attribute, name in RESULTS_MAPPER.items():
        response.append({'name': name, 'value': getattr(results, attribute)})

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
    'predictionMode': list(PREDICTION_DATA_PATHS.keys()),
    }
    return jsonify(config)

@app.route("/step/{}".format(STATUS_START), methods = ['POST'])
def start_simulation():
    updated_settings = request.json['settings']
    for attribute, name in SETTINGS_UI_MAPPER.items():
        setattr(simulator.settings, attribute, updated_settings[name])
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
    return jsonify(get_step_response())

@app.route("/step/{}".format(STATUS_FINISH), methods = ['POST'])
def finish_simulation():
    results = get_results()
    simulator.finish_simulation()
    return jsonify(get_finish_simulation_response(results))

@app.route("/advance/<steps>".format(STATUS_FINISH), methods = ['POST'])
def advance_steps(steps):
    # Start simulation if settings in response
    if "settings" in request.json:
        updated_settings = request.json['settings']
        for attribute, name in SETTINGS_UI_MAPPER.items():
            setattr(simulator.settings, attribute, updated_settings[name])
        simulator.start_simulation()

    for i in range(int(steps)):
        # Skip if start and cycle count is 0
        if "settings" not in request.json or i != 0:
            simulator.next_cycle()
        simulator.rebalance()
        simulator.simulate_rides()
    return jsonify(get_step_response())

@app.route("/download", methods = ['GET'])
def download_results():
    results_path = os.path.join(RESULTS_PATH, str(simulator.simulation_start_time))
    zipdir(results_path)
    return send_file(results_path + '.zip',
                        mimetype = 'application/zip',
                        attachment_filename= results_path + '.zip',
                        as_attachment = True)

@app.route("/download/<unix_time>", methods = ['GET'])
def download_result(unix_time):
    results_path = os.path.join(RESULTS_PATH, unix_time)
    zipdir(results_path)
    return send_file(results_path + '.zip',
                        mimetype = 'application/zip',
                        attachment_filename= results_path + '.zip',
                        as_attachment = True)

@app.route("/delete/<unix_time>", methods = ['GET'])
def detele_result(unix_time):
    results_path = os.path.join(RESULTS_PATH, unix_time)
    try:
        shutil.rmtree(results_path)
        response = jsonify(success=True)
        response.status_code = 200
    except Exception as e:
        response = jsonify(success=False)
        response.status_code = 401

    try:
        shutil.rmtree(results_path + '.zip')
    except Exception as e:
        print(e)

    return response


@app.route("/records", methods = ['GET'])
def get_simulation_records():
    return jsonify(simulator.get_all_simulation_records())

def zipdir(path):
    zipf = zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()


if __name__ == "__main__":
    app.run(debug=True)
