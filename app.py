from flask import Flask, jsonify

from services.simulator import Simulator

app = Flask(__name__)

simulator = Simulator()

def get_stations_response():
    stations = []

    for station_snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_response = {}
        station = station_snapshot.station
        station_response['name'] = station.name
        station_response['id'] = station.id
        station_response['count'] = station_snapshot.available_bike_count_before_rebalance
        station_response['coordinates'] = station.coordinates
        stations.append(station_response)

    return stations

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

def get_station_snapshots():
    station_snapshots = []

    for snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_snapshot = {}
        station = snapshot.station
        station_snapshot['id'] = station.id
        station_snapshot['count'] = snapshot.available_bike_count_before_rebalance
        station_snapshots.append(station_snapshot)

    return station_snapshots

def get_next_cycle_response():
    current_cycle = simulator.simulation.cycles[-1]
    cycle_snapshot = {}
    cycle_snapshot['count'] = current_cycle.count
    cycle_snapshot['time'] = current_cycle.time

    previous_cycle = simulator.simulation.cycles[-2]
    cycle_snapshot['moved_bike_count'] = previous_cycle.moved_bike_count
    cycle_snapshot['rebalanced_bike_count'] = previous_cycle.rebalanced_bike_count
    cycle_snapshot['rebalance_cost'] = previous_cycle.rebalance_cost
    cycle_snapshot['cumulative_moved_bike_count'] = previous_cycle.cumulative_moved_bike_count
    cycle_snapshot['cumulative_rebalanced_bike_count'] = previous_cycle.cumulative_rebalanced_bike_count
    cycle_snapshot['cumulative_rebalance_cost'] = previous_cycle.cumulative_rebalance_cost
    cycle_response = {}
    cycle_response['cycle_snapshot'] = cycle_snapshot

    station_snapshots = get_station_snapshots()
    cycle_response['station_snapshots'] = station_snapshots

    return cycle_response

@app.route("/initialize")
def initialize():
    simulator.initialize_simulation()
    return jsonify(get_stations_response())

@app.route("/rebalance")
def rebalance():
    simulator.rebalance()
    return jsonify(get_trips_response())

@app.route("/next-cycle")
def next_cycle():
    simulator.next_cycle()
    return jsonify(get_next_cycle_response())

if __name__ == "__main__":
    app.run(debug=True)
