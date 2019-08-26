from flask import Flask, jsonify

from models.simulation import Simulation
from models.setting import Setting
from services.simulator import Simulator

app = Flask(__name__)

simulator = Simulator()

def get_station_data():
    stations_dict = []

    for station_snapshot in simulator.simulation.cycles[-1].station_snapshots:
        station_data = {}
        station = station_snapshot.station
        station_data['name'] = station.name
        station_data['id'] = station.id
        station_data['count'] = station_snapshot.available_bike_count_before_rebalance
        station_data['coordinates'] = station.coordinates
        stations_dict.append(station_data)

    return stations_dict

@app.route("/initialize")
def initialize():
    simulator.initialize_simulation()
    return jsonify(get_station_data())

@app.route("/rebalance")
def rebalance():
    simulator.rebalance()
    return "hello"

@app.route("/nextCycle")
def next_cycle():
    simulator.next_cycle()
    return "hello"

if __name__ == "__main__":
    app.run(debug=True)
