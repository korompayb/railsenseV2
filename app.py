from flask import Flask, render_template, request, url_for
import requests
import time
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    manifest_url = url_for('static', filename='manifest.json')
    
    # Első API hívás
    arrivals_url = "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon=18.057539&clientLat=47.046356&minutesAfter=20&onlyDepartures=false&limit=60&lat=47.046356&lon=18.057539&radius=2000&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
    arrivals_response = requests.get(arrivals_url)
    
    trainsdata = []
    added_trains = set()  # Ez tárolja azokat a vonatokat, amelyeket már hozzáadtunk
    result_status = 2  # Alapértelmezett érték: nincs vonat
    message = ""

    if arrivals_response.status_code == 200:
        data = arrivals_response.json()['data']['list']
        routes_data = arrivals_response.json()['data']['references']['routes']
        
        for item in data:
            route_id = item['routeId']
            headsign = item['headsign']
            stop_times = item['stopTimes']
            
            if route_id in routes_data:
                route_info = routes_data[route_id]
                short_name = route_info.get('shortName', 'N/A')
                description = route_info.get('description', 'N/A')
                color = route_info.get('color', 'N/A')
            else:
                short_name = "N/A"
                description = "N/A"
                
            for stop_time in stop_times:
                train_id = stop_time['tripId']
                if train_id not in added_trains:
                    arrival_time = time.strftime(' %H:%M', time.localtime(stop_time['arrivalTime']))
                    departure_time = time.strftime('%H:%M', time.localtime(stop_time['departureTime']))
                    
                    predicted_arrival_time = None
                    if 'predictedArrivalTime' in stop_time:
                        predicted_arrival_time = time.strftime('%H:%M', time.localtime(stop_time['predictedArrivalTime']))
                        # Ha a headsign 'Budapest-Déli', akkor vonjunk ki 5 percet, különben adjunk hozzá 5 percet
                        if headsign != "Budapest-Déli":
                            predicted_arrival_time = (datetime.datetime.strptime(predicted_arrival_time, '%H:%M') - datetime.timedelta(minutes=5)).strftime('%H:%M')
                        else:
                            predicted_arrival_time = (datetime.datetime.strptime(predicted_arrival_time, '%H:%M') + datetime.timedelta(minutes=5)).strftime('%H:%M')
                    else:
                        predicted_arrival_time = arrival_time
                    
                    # Második API hívás
                    trip_details_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/trip-details?tripId={train_id}&version=4&includeReferences=stops&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
                    trip_details_response = requests.get(trip_details_url)
                    
                    trip_details = []
                    if trip_details_response.status_code == 200:
                        trip_details_data = trip_details_response.json()['data']['entry']['stopTimes']
                        stops_data = trip_details_response.json()['data']['references']['stops']
                        
                        for stop in trip_details_data:
                            stop_id = stop['stopId']
                            stop_info = stops_data.get(stop_id, {})
                            trip_details.append({
                                'stop_id': stop_id,
                                'stop_name': stop_info.get('name', 'N/A'),
                                'stop_lat': stop_info.get('lat', 'N/A'),
                                'stop_lon': stop_info.get('lon', 'N/A'),
                                'arrival_time': time.strftime('%H:%M', time.localtime(stop['arrivalTime'])) if 'arrivalTime' in stop else time.strftime('%H:%M', time.localtime(stop['departureTime'])),
                                'departure_time': time.strftime('%H:%M', time.localtime(stop['departureTime'])) if 'departureTime' in stop else 'N/A',
                                'predicted_arrival_time': time.strftime('%H:%M', time.localtime(stop['predictedArrivalTime'])) if 'predictedArrivalTime' in stop else 'N/A',
                                'predicted_departure_time': time.strftime('%H:%M', time.localtime(stop['predictedDepartureTime'])) if 'predictedDepartureTime' in stop else 'N/A'
                            })
                    
                    trainsdata.append({
                        'route_id': route_id,
                        'headsign': headsign,
                        'stop_id': stop_time['stopId'],
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'predicted_arrival_time': predicted_arrival_time,
                        'short_name': short_name,
                        'description': description,
                        'color': color,
                        'trip_details': trip_details  # Második API válaszának hozzáadása
                    })
                    added_trains.add(train_id)
                    result_status = 1  # Vonat észlelve
    elif arrivals_response.status_code != 200:
        message = "404 Hiba az oldalon"
        result_status = 3
    
    return render_template('index.html', trainsdata=trainsdata, result_status=result_status, manifest_url=manifest_url, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
