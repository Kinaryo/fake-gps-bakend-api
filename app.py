import os
import datetime
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import haversine, get_next_id, get_last_data  # Import utility functions

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data/data.csv'
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    try:
        current_timestamp = datetime.datetime.fromisoformat(data['timestamp'].replace("Z", "+00:00"))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid timestamp format'}), 400

    current_lat = data['latitude']
    current_lon = data['longitude']
    accuracy = data['accuracy']

    delta_time, distance, speed, anomaly = None, 0, None, False
    last_data = get_last_data(DATA_FILE)

    if last_data:
        delta_time = (current_timestamp - last_data['timestamp']).total_seconds()
        distance = haversine(last_data['latitude'], last_data['longitude'], current_lat, current_lon)
        if delta_time > 0:
            speed = (distance / (delta_time / 3600))
        if speed and speed > 1000 or (distance > 1000 and delta_time < 3600):
            anomaly = True

    with open(DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:
            writer.writerow(['id', 'latitude', 'longitude', 'accuracy', 'timestamp', 'delta_time', 'distance', 'speed', 'ip', 'label', 'anomaly', 'from_to'])
        from_to = f"From ({last_data['latitude']}, {last_data['longitude']}) to ({current_lat}, {current_lon})" if last_data else "N/A"
        writer.writerow([get_next_id(DATA_FILE), current_lat, current_lon, accuracy, data['timestamp'], delta_time, distance, speed, data['ip'], data['label'], anomaly, from_to])

    return jsonify({'status': 'success', 'message': 'Data saved successfully!', 'anomaly': anomaly, 'distance': distance, 'from_to': from_to})

@app.route('/data', methods=['GET'])
def get_data():
    order = request.args.get('order', 'desc')
    data_list = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            rows.sort(key=lambda x: datetime.datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")), reverse=(order == 'desc'))
            data_list.extend(rows)
    return jsonify(data_list)

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_data(id):
    rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in list(reader) if int(row['id']) != id]
        with open(DATA_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'latitude', 'longitude', 'accuracy', 'timestamp', 'delta_time', 'distance', 'speed', 'ip', 'label', 'anomaly', 'from_to'])
            writer.writeheader()
            writer.writerows(rows)
    return jsonify({'status': 'success', 'message': f'Data with ID {id} has been deleted.'})

@app.route('/delete_all', methods=['DELETE'])
def delete_all_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return jsonify({'status': 'success', 'message': 'All data has been deleted.'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
