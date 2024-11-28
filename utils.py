import math
import os
import datetime
import csv

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_next_id(data_file):
    if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
        with open(data_file, 'r') as csvfile:
            rows = list(csv.DictReader(csvfile))
            if rows:
                return int(rows[-1]['id']) + 1
    return 1

def get_last_data(data_file):
    if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
        with open(data_file, 'r') as csvfile:
            rows = list(csv.DictReader(csvfile))
            if rows:
                last_row = rows[-1]
                return {
                    'latitude': float(last_row['latitude']),
                    'longitude': float(last_row['longitude']),
                    'timestamp': datetime.datetime.fromisoformat(last_row['timestamp'].replace("Z", "+00:00"))
                }
    return None
