from flask import Flask, render_template, request, url_for
import requests
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    manifest_url = url_for('static', filename='manifest.json')
    url = "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon=18.057539&clientLat=47.046356&minutesAfter=10&stopId=BKK_005504358_0&onlyDepartures=false&limit=60&lat=47.046356&lon=18.057539&radius=2000&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
    response = requests.get(url)
    trainsdata = []
    added_trains = set()  # Ez tárolja azokat a vonatokat, amelyeket már hozzáadtunk
    result_status = 2  # Alapértelmezett érték: nincs vonat
    message = ""

    if response.status_code == 200:
        data = response.json()['data']['list']
        routes_data = response.json()['data']['references']['routes']
        
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
                    arrival_time = time.strftime(' %H:%M:%S', time.localtime(stop_time['arrivalTime']))
                    departure_time = time.strftime('%H:%M:%S', time.localtime(stop_time['departureTime']))
                    
                    predicted_arrival_time = None
                    if 'predictedArrivalTime' in stop_time:
                        predicted_arrival_time = time.strftime('%H:%M:%S', time.localtime(stop_time['predictedArrivalTime']))
                    else:
                        predicted_arrival_time = arrival_time
                    
                    
                    trainsdata.append({
                        'route_id': route_id,
                        'headsign': headsign,
                        'stop_id': stop_time['stopId'],
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'predicted_arrival_time': predicted_arrival_time,
                        'short_name': short_name,
                        'description': description,
                        'color': color
                    })
                    added_trains.add(train_id)
                    result_status = 1  # Vonat észlelve
    elif response.status_code != 200:
        message = "404 Hiba az oldalon"
        result_status = 3
    return render_template('index.html', trainsdata=trainsdata ,result_status=result_status, manifest_url = manifest_url, message = message)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
