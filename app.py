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
        station_response['count'] = station_snapshot.available_bike_count_before_rebalance
        station_response['coordinates'] = station.coordinates
        stations.append(station_response)

    return stations

def get_initialize_response():
    initialize_response = {}

    initialize_response['stations'] = get_stations_response()
    initialize_response['setting'] = simulator.simulation.setting.__dict__

    return initialize_response

def get_trips_response():
    trips = []

    for trip in simulator.simulation.cycles[-1].trips:
        trip_data = {}
        trip_data['id'] = trip.id
        trip_data['source_id'] = trip.source.id
        trip_data['destination_id'] = trip.destination.id
        trip_data['count'] = trip.rebalanced_bike_count
        trips.append(trip_data)

    return trips

def get_cycle_snapshot():
    cycle_snapshot = {}

    current_cycle = simulator.simulation.cycles[-1]

    cycle_snapshot['count'] = current_cycle.count
    cycle_snapshot['time'] = current_cycle.time
    cycle_snapshot['moved_bike_count'] = current_cycle.moved_bike_count
    cycle_snapshot['rebalanced_bike_count'] = current_cycle.rebalanced_bike_count
    cycle_snapshot['rebalance_cost'] = current_cycle.rebalance_cost
    cycle_snapshot['cumulative_moved_bike_count'] = current_cycle.cumulative_moved_bike_count
    cycle_snapshot['cumulative_rebalanced_bike_count'] = current_cycle.cumulative_rebalanced_bike_count
    cycle_snapshot['cumulative_rebalance_cost'] = current_cycle.cumulative_rebalance_cost

    return cycle_snapshot

def get_rebalance_response():
    rebalance_response = {}

    rebalance_response['cycle_snapshot'] = get_cycle_snapshot()
    rebalance_response['trips'] = get_trips_response()

    return rebalance_response

def get_station_snapshots():
    station_snapshots = []

    for snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_snapshot = {}
        station = snapshot.station
        station_snapshot['id'] = station.id
        station_snapshot['count'] = snapshot.available_bike_count_before_rebalance
        station_snapshots.append(station_snapshot)

    return station_snapshots

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
