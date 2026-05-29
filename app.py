from flask import Flask, render_template, request, url_for, session, redirect, jsonify
import requests
import datetime
import pytz
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

DEFAULT_LAT = 47.046356
DEFAULT_LON = 18.057539
DEFAULT_RADIUS = 2000
DEFAULT_ADDRESS = "Balatonfűzfő"

hungary_tz = pytz.timezone('Europe/Budapest')

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'c01a7a32d2b862992d67500569e20363')
BKK_API_KEY = os.environ.get('BKK_API_KEY', '7ff7c954-05d3-4dd2-93b6-cb714dcdca69')


def get_weather_data(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
    )
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return {
                'temperature': round(d['main']['temp']),
                'description': d['weather'][0]['description'].capitalize(),
                'feels_like': round(d['main']['feels_like']),
                'icon_code': d['weather'][0]['icon'],
                'wind_speed': round(d['wind']['speed'] * 3.6, 2),
            }
    except Exception:
        pass
    return None


def _sort_key(train, now):
    """Sort trains chronologically from now, safe across midnight."""
    t_str = train.get('predicted_arrival_time', 'N/A')
    if t_str == 'N/A':
        return datetime.timedelta(days=999)
    try:
        h, m = map(int, t_str.split(':'))
        t_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if t_dt <= now:
            t_dt += datetime.timedelta(days=1)
        return t_dt - now
    except ValueError:
        return datetime.timedelta(days=999)


def fetch_trains(lat, lon, radius):
    """Fetch live RAIL trains near location. Returns (trains, result_status, message)."""
    arrivals_url = (
        f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location"
        f"?clientLon={lon}&clientLat={lat}&lat={lat}&lon={lon}&radius={radius}"
        f"&minutesBefore=0&minutesAfter=60&stopTimeType=ARRIVAL_AND_DEPARTURE"
        f"&includeRouteTypes=RAIL&includeVehicleFromTrip=true"
        f"&limit=60&minResult=1&version=2&includeReferences=true&appVersion=1.1.abc"
        f"&key={BKK_API_KEY}"
    )
    vehicles_url = (
        f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/vehicles-for-location"
        f"?clientLon={lon}&clientLat={lat}&lat={lat}&lon={lon}&radius={radius}"
        f"&includeRouteTypes=RAIL&limit=60&minResult=1"
        f"&version=2&includeReferences=true&appVersion=1.1.abc&key={BKK_API_KEY}"
    )

    arrivals_resp = vehicles_resp = None
    try:
        arrivals_resp = requests.get(arrivals_url, timeout=8)
        vehicles_resp = requests.get(vehicles_url, timeout=8)
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")

    trainsdata = []
    added_trains = set()
    result_status = 2
    message = ""

    if arrivals_resp and arrivals_resp.status_code == 200:
        try:
            arrivals_json = arrivals_resp.json()
            arrivals_data = arrivals_json['data']['list']
            routes_data = arrivals_json['data']['references']['routes']
            vehicles_list = []
            if vehicles_resp and vehicles_resp.status_code == 200:
                vehicles_list = vehicles_resp.json().get('data', {}).get('list', [])

            for item in arrivals_data:
                route_id = item['routeId']
                headsign = item['headsign']
                route_info = routes_data.get(route_id, {})

                # Vehicle data embedded via includeVehicleFromTrip=true
                inline_vehicle = item.get('vehicle') or {}
                vehicle_name = inline_vehicle.get('style', {}).get('icon', {}).get('name', 'N/A')
                vehicletype = inline_vehicle.get('style', {}).get('vehicleIcon', {}).get('name', 'RAIL')
                vehicle_label = inline_vehicle.get('model', 'N/A')
                stop_sequence = inline_vehicle.get('stopSequence', 'N/A')

                for stop_time in item['stopTimes']:
                    train_id = stop_time['tripId']
                    if train_id in added_trains:
                        continue

                    ts_arrival = stop_time.get('arrivalTime', stop_time.get('departureTime'))
                    arrival_time = datetime.datetime.fromtimestamp(ts_arrival, tz=hungary_tz).strftime('%H:%M')
                    departure_time = (
                        datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M')
                        if 'departureTime' in stop_time else 'N/A'
                    )
                    ts_pred = stop_time.get('predictedArrivalTime', ts_arrival)
                    predicted_arrival_time = datetime.datetime.fromtimestamp(ts_pred, tz=hungary_tz).strftime('%H:%M')

                    vehicle_data = next((v for v in vehicles_list if v.get('tripId') == train_id), {})
                    now = datetime.datetime.now(tz=hungary_tz)
                    pred_dt = datetime.datetime.fromtimestamp(ts_pred, tz=hungary_tz)
                    mins = int((pred_dt - now).total_seconds() // 60)
                    if mins > 0:
                        mins_text = f"{mins} perc múlva érkezik"
                    elif mins == 0:
                        mins_text = "Most érkezik"
                    else:
                        mins_text = "Már elment"

                    trainsdata.append({
                        'trip_id': train_id,
                        'route_id': route_id,
                        'headsign': headsign,
                        'stop_id': stop_time['stopId'],
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'predicted_arrival_time': predicted_arrival_time,
                        'predicted_departure_time': stop_time.get('predictedDepartureTime', 'N/A'),
                        'predicted_arrival_minutes': mins_text,
                        'short_name': route_info.get('shortName', 'N/A'),
                        'description': route_info.get('description', 'N/A'),
                        'stop_sequence': stop_sequence,
                        'type': route_info.get('type', 'RAIL'),
                        'color': route_info.get('color', '808080'),
                        'text_color': route_info.get('textColor', 'FFFFFF'),
                        'vehicle_name': vehicle_name,
                        'vehicle_label': vehicle_label,
                        'vehicletype': vehicletype,
                        'trip_details': [],
                        'vehicle_lat': vehicle_data.get('lat', 'N/A'),
                        'vehicle_lon': vehicle_data.get('lon', 'N/A'),
                        'source': 'online',
                    })
                    added_trains.add(train_id)
            result_status = 1
        except Exception as e:
            message = f"Hiba az online adatok feldolgozásakor: {e}"
            result_status = 3
    else:
        message = "Online API nem elérhető."
        result_status = 3

    now = datetime.datetime.now(tz=hungary_tz)
    sorted_trains = sorted(trainsdata, key=lambda t: _sort_key(t, now))
    return sorted_trains, result_status, message


# ── New API endpoints ────────────────────────────────────────────────────────

@app.route('/api/location', methods=['POST'])
def api_location():
    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': 'No JSON body'}), 400
    try:
        lat = float(data.get('lat', DEFAULT_LAT))
        lon = float(data.get('lon', DEFAULT_LON))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Invalid lat/lon'}), 400

    address = DEFAULT_ADDRESS
    try:
        r = requests.get(
            f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}',
            headers={'User-Agent': 'RailSense/1.0'},
            timeout=5,
        )
        if r.status_code == 200:
            address = r.json().get('display_name', address)
    except Exception:
        pass

    session['lat'] = lat
    session['lon'] = lon
    session['address'] = address
    return jsonify({'ok': True, 'address': address, 'lat': lat, 'lon': lon})


@app.route('/api/trip-details/<trip_id>')
def api_trip_details(trip_id):
    url = (
        f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/trip-details"
        f"?tripId={trip_id}&version=4&includeReferences=stops&key={BKK_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=8)
    except Exception:
        return jsonify({'ok': False, 'stops': []})
    if resp.status_code != 200:
        return jsonify({'ok': False, 'stops': []})
    try:
        tj = resp.json()
        entry = tj.get('data', {}).get('entry', {})
        stops_ref = tj.get('data', {}).get('references', {}).get('stops', {})
        stops = []
        for stop in entry.get('stopTimes', []):
            sid = stop['stopId']
            si = stops_ref.get(sid, {})
            s_ts = stop.get('arrivalTime', stop.get('departureTime'))
            s_pred_ts = stop.get('predictedArrivalTime', s_ts)
            stops.append({
                'stop_id': sid,
                'stop_name': si.get('name', 'N/A'),
                'arrival_time': datetime.datetime.fromtimestamp(s_ts, tz=hungary_tz).strftime('%H:%M') if s_ts else 'N/A',
                'predicted_arrival_time': datetime.datetime.fromtimestamp(s_pred_ts, tz=hungary_tz).strftime('%H:%M') if s_pred_ts else 'N/A',
                'stopseqe2': stop.get('stopSequence'),
            })
        return jsonify({'ok': True, 'stops': stops})
    except Exception as e:
        return jsonify({'ok': False, 'stops': [], 'error': str(e)})


@app.route('/api/trains')
def api_trains():
    lat = float(session.get('lat', DEFAULT_LAT))
    lon = float(session.get('lon', DEFAULT_LON))
    radius = int(session.get('radius', DEFAULT_RADIUS))
    address = session.get('address', DEFAULT_ADDRESS)
    trains, status, msg = fetch_trains(lat, lon, radius)
    weather = get_weather_data(lat, lon)
    return jsonify({
        'trains': trains,
        'result_status': status,
        'message': msg,
        'address': address,
        'weather': weather,
    })


# ── Legacy redirects ─────────────────────────────────────────────────────────

@app.route('/fullscreen_map')
@app.route('/railsense', methods=['GET', 'POST'])
def legacy_redirect():
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')

""" weather report
API/TRAINS

{
  "address": "110, Balaton k\u00f6r\u00fat, Balatonkenese, Balatonalm\u00e1di j\u00e1r\u00e1s, Veszpr\u00e9m v\u00e1rmegye, K\u00f6z\u00e9p-Dun\u00e1nt\u00fal, Dun\u00e1nt\u00fal, 8174, Magyarorsz\u00e1g",
  "message": "",
  "result_status": 1,
  "trains": [],
  "weather": {
    "description": "Tiszta \u00e9gbolt",
    "feels_like": 16,
    "icon_code": "01n",
    "temperature": 17,
    "wind_speed": 7.02
  }
}

 """

@app.route('/report')
def report():
    lat = float(session.get('lat', DEFAULT_LAT))
    lon = float(session.get('lon', DEFAULT_LON))
    address = session.get('address', DEFAULT_ADDRESS)
    manifest_url = url_for('static', filename='manifest.json')

    weather_report = get_weather_data(lat, lon)

    return render_template(
        'report.html',
        lat=lat, lon=lon, address=address, weather_report=weather_report,
        manifest_url=manifest_url,
    )


@app.route('/')
def fullscreen_map():
    lat = float(session.get('lat', DEFAULT_LAT))
    lon = float(session.get('lon', DEFAULT_LON))
    address = session.get('address', DEFAULT_ADDRESS)
    manifest_url = url_for('static', filename='manifest.json')

    return render_template(
        'fullscreen_map.html',
        lat=lat, lon=lon, address=address,
        manifest_url=manifest_url,
    )


if __name__ == '__main__':
    app.run(port=10000, debug=True)
