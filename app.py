from flask import Flask, jsonify, request

from services.simulator import Simulator

app = Flask(__name__)

simulator = Simulator()

def get_stations_response():
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

def get_statistics():
    cycle_snapshot = {}

    current_cycle = simulator.simulation.cycles[-1]

    cycle_snapshot['count'] = current_cycle.count
    cycle_snapshot['time'] = current_cycle.time
    cycle_snapshot['moved_bike_count'] = current_cycle.moved_bike_count
    cycle_snapshot['rebalanced_bike_count'] = current_cycle.rebalanced_bike_count
    cycle_snapshot['rebalance_cost'] = current_cycle.rebalance_cost
    cycle_snapshot['lyapunov'] = current_cycle.lyapunov
    cycle_snapshot['lyapunov_drift'] = current_cycle.lyapunov_drift
    cycle_snapshot['cumulative_moved_bike_count'] = current_cycle.cumulative_moved_bike_count
    cycle_snapshot['cumulative_rebalanced_bike_count'] = current_cycle.cumulative_rebalanced_bike_count
    cycle_snapshot['cumulative_rebalance_cost'] = current_cycle.cumulative_rebalance_cost
    cycle_snapshot['cumulative_drift'] = current_cycle.cumulative_drift
    cycle_snapshot['time_avg_rebalance_cost'] = current_cycle.time_avg_rebalance_cost
    cycle_snapshot['time_avg_cond_drift'] = current_cycle.time_avg_cond_drift

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

def get_init_response():
    response = {}
    response['current_status'] = simulator.simulation.status
    response['next_status'] = simulator.simulation.next_status

    return response

def get_rebalance_response():
    response = {}
    response['current_status'] = simulator.simulation.status
    response['next_status'] = simulator.simulation.next_status
    response['rebalance_schedules'] = get_rebalance_schedules_response()
    response['statistics'] = get_statistics()
    response['stations'] = get_station_snapshots()

    return response

def get_simulate_rides_response():
    response = {}
    response['current_status'] = simulator.simulation.status
    response['next_status'] = simulator.simulation.next_status
    response['statistics'] = get_statistics()
    response['stations'] = get_station_snapshots()

    return response

def get_next_cycle_response():
    response = {}
    response['current_status'] = simulator.simulation.status
    response['next_status'] = simulator.simulation.next_status
    response['statistics'] = get_statistics()

    return response

def get_finish_simulation_response():
    return simulator.simulation.result.__dict__

def get_status_response():
    response = {}
    response['current_status'] = simulator.simulation.status
    response['next_status'] = simulator.simulation.next_status
    response['statistics'] = get_statistics()
    response['stations'] = get_station_snapshots()

    return response

@app.route("/initialize")
def initialize():
    return jsonify(get_init_response())

@app.route("/setting", methods = ['GET'])
def get_setting():
    return jsonify(simulator.simulation.setting.__dict__)

@app.route("/setting", methods = ['POST'])
def configure_setting():
    setting = request.form
    for key, value in setting.items():
        setattr(simulator.simulation.setting, key, value )
    return jsonify(simulator.simulation.setting.__dict__)

@app.route("/stations", methods = ['GET'])
def get_stations():
    return jsonify(get_stations_response)

@app.route("/step/start")
def start_simulation():
    simulator.start_simulation()
    return jsonify(get_next_cycle_response())

@app.route("/step/next-cycle")
def next_cycle():
    simulator.next_cycle()
    return jsonify(get_next_cycle_response())

@app.route("/step/rebalance")
def rebalance():
    simulator.rebalance()
    return jsonify(get_rebalance_response())

@app.route("/step/rides")
def simulate_rides():
    simulator.simulate_rides()
    return jsonify(get_simulate_rides_response())

@app.route("/step/finish")
def finish_simulation():
    simulator.finish_simulation()
    return jsonify(get_finish_simulation_response())

@app.route("/status")
def get_status():
    return jsonify(get_status_response())

if __name__ == "__main__":
    app.run(debug=True)
