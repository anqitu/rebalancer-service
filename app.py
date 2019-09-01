from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS

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
    return simulator.setting.__dict__

def get_rebalance_schedules():
    rebalance_schedules = []

    for schedule in simulator.simulation.cycles[-1].rebalance_schedules:
        rebalance_schedule = {}
        rebalance_schedule['id'] = schedule.id
        rebalance_schedule['source_id'] = schedule.source.id
        rebalance_schedule['destination_id'] = schedule.destination.id
        rebalance_schedule['count'] = schedule.rebalanced_bike_count
        rebalance_schedules.append(rebalance_schedule)

    return rebalance_schedules

def get_statistics():
    statistics = []

    current_cycle = simulator.simulation.cycles[-1]

    for attribute, name in {'count': 'Cycle Count',
                            'moved_bike_count': 'Moved Bike',
                            'cumulative_moved_bike_count': 'Cumulative Moved Bike',
                            'rebalanced_bike_count': 'Rebalanced Bike',
                            'cumulative_rebalanced_bike_count': 'Cumulative Rebalanced Bike',
                            'rebalance_cost': 'Rebalanced Cost',
                            'cumulative_rebalance_cost': 'Cumulative Rebalance Cost',
                            'time_avg_rebalance_cost': 'Time Average Rebalance Cost',
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
        response['rebalanceSchedules'] = get_rebalance_schedules()

    elif response['currentStatus'] == STATUS_RIDES:
        response['statistics'] = get_statistics()
        response['stations'] = get_station_snapshots()

    return response

def get_simulate_rides_response():
    response = {}
    response['currentStatus'] = simulator.simulation.current_status
    response['nextStatus'] = simulator.simulation.next_status
    response['statistics'] = get_statistics()
    response['stations'] = get_station_snapshots()

    return response

def get_next_cycle_response():
    response = {}
    response['currentStatus'] = simulator.simulation.current_status
    response['nextStatus'] = simulator.simulation.next_status
    response['statistics'] = get_statistics()

    return response

def get_finish_simulation_response():
    return simulator.get_result().__dict__


@app.route("/status", methods = ['GET'])
def get_status():
    return jsonify(get_status_response())

@app.route("/step/{}".format(STATUS_START), methods = ['POST'])
def start_simulation():
    setting = request.form
    for key, value in setting.items():
        setattr(simulator.setting, key, value)
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

@app.route("/finish", methods = ['POST'])
def finish_simulation():
    response = get_finish_simulation_response()
    simulator.finish_simulation()
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
