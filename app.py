from flask import Flask, jsonify, request

from services.simulator import Simulator

app = Flask(__name__)

simulator = Simulator()

def get_stations_response():
    stations = []

    for station_snapshot in simulator.station_snapshots:
        station_response = {}
        station = station_snapshot.station
        station_response['name'] = station.name
        station_response['id'] = station.id
        station_response['coordinates'] = station.coordinates
        station_response['capacity'] = station.capacity
        station_response['count'] = station_snapshot.available_bike_count_before_rebalance
        stations.append(station_response)

    return stations

def get_initialize_response():
    initialize_response = {}

    initialize_response['stations'] = get_stations_response()
    initialize_response['setting'] = simulator.simulation.setting.__dict__

    return initialize_response

def get_rebalance_schedules_response():
    rebalance_schedules = []

    for rebalance_schedule in simulator.simulation.cycles[-1].rebalance_schedules:
        rebalance_schedule_response = {}
        rebalance_schedule_response['id'] = rebalance_schedule.id
        rebalance_schedule_response['source_id'] = rebalance_schedule.source.id
        rebalance_schedule_response['destination_id'] = rebalance_schedule.destination.id
        rebalance_schedule_response['count'] = rebalance_schedule.rebalanced_bike_count
        rebalance_schedules.append(rebalance_schedule_response)

    return rebalance_schedules

def get_cycle_snapshot():
    cycle_snapshot = {}

    current_cycle = simulator.simulation.cycles[-1]

    cycle_snapshot['count'] = current_cycle.count
    cycle_snapshot['time'] = current_cycle.time
    cycle_snapshot['moved_bike_count'] = current_cycle.moved_bike_count
    cycle_snapshot['rebalanced_bike_count'] = current_cycle.rebalanced_bike_count
    cycle_snapshot['rebalance_cost'] = current_cycle.rebalance_cost
    cycle_snapshot['drift'] = current_cycle.drift
    cycle_snapshot['cumulative_moved_bike_count'] = current_cycle.cumulative_moved_bike_count
    cycle_snapshot['cumulative_rebalanced_bike_count'] = current_cycle.cumulative_rebalanced_bike_count
    cycle_snapshot['cumulative_rebalance_cost'] = current_cycle.cumulative_rebalance_cost
    cycle_snapshot['cumulative_drift'] = current_cycle.cumulative_drift

    return cycle_snapshot

def get_station_snapshots():
    station_snapshots = []

    for snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_snapshot = {}
        station = snapshot.station
        station_snapshot['id'] = station.id
        station_snapshot['count'] = snapshot.current_bike_count
        station_snapshots.append(station_snapshot)

    return station_snapshots

def get_rebalance_response():
    rebalance_response = {}

    rebalance_response['rebalance_schedules'] = get_rebalance_schedules_response()
    rebalance_response['cycle_snapshot'] = get_cycle_snapshot()
    rebalance_response['station_snapshots'] = get_station_snapshots()

    return rebalance_response

def get_simulate_ride_response():
    cycle_response = {}
    cycle_response['cycle_snapshot'] = get_cycle_snapshot()
    cycle_response['station_snapshots'] = get_station_snapshots()

    return cycle_response

@app.route("/initialize")
def initialize():
    return jsonify(get_initialize_response())

@app.route("/configure-setting", methods = ['POST'])
def configure_setting():
    setting = request.form
    for key, value in setting.items():
        setattr(simulator.simulation.setting, key, value )
    return jsonify(simulator.simulation.setting.__dict__)

@app.route("/start-simulation")
def start_simulation():
    simulator.start_simulation()
    return jsonify(get_cycle_snapshot())

@app.route("/next-cycle")
def next_cycle():
    simulator.next_cycle()
    return jsonify(get_cycle_snapshot())

@app.route("/rebalance")
def rebalance():
    simulator.rebalance()
    return jsonify(get_rebalance_response())

@app.route("/simulate-rides")
def simulate_rides():
    simulator.simulate_rides()
    return jsonify(get_simulate_ride_response())

if __name__ == "__main__":
    app.run(debug=True)
