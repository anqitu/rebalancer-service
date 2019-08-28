from geopy.distance import distance

def calculate_distance_between_stations(source, destination):
    return distance((source.coordinates[1],source.coordinates[0]),
                    (destination.coordinates[1], destination.coordinates[0])).km
