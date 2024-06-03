from flask import Flask, render_template, request, url_for, session, redirect
import requests
import datetime
import pytz

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

radius = 2000


lat = 47.046356
lon = 18.057539

# Set timezone to Hungary
hungary_tz = pytz.timezone('Europe/Budapest')

def get_weather_data(city):
    api_key = 'c01a7a32d2b862992d67500569e20363'
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=hu"
    response = requests.get(weather_url)
    if response.status_code == 200:
        data = response.json()
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        icon_code = data['weather'][0]['icon']
        desc = data['weather'][0]['description']
        wind_speed = data['wind']['speed']  # Convert m/s to km/h
        wind_speed = round(wind_speed, 2)  # Round the wind speed to 2 decimal places
        return {
            'temperature': temperature,
            'description': desc.capitalize(),
            'feels_like': feels_like,
            'icon_code': icon_code,
            'wind_speed': wind_speed * 3.6
        }
    else:
        return None



@app.route('/update_radius', methods=['POST'])
def update_radius():
    radius = request.form.get('radius', '2000')  # Alapértelmezett érték: 2000
    print(radius)
    session['radius'] = radius
    return render_template('maps.html')

@app.route('/')
def search():
    return render_template('maps.html')

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    try:
        lat = request.form['lat']
    except KeyError:
        lat = 47.046356
        return render_template("maps.html")
    
    try:
        lon = request.form['lon']
    except KeyError:
        lon = 18.057539
        return render_template("maps.html")
    

    try:
        address = request.form['address']
    except KeyError:
        address = "Balatonfűzfő"
        render_template("maps.html")

    session['lat'] = lat
    session['lon'] = lon
    session['address'] = address

    

    print(lat, lon)
    # Új koordináták használata az API-hívásokban
    # Például:
    # arrivals_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon={lon}&clientLat={lat}&minutesAfter=30&onlyDepartures=false&limit=60&lat={lat}&lon={lon}&radius=2000&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"

    # Vagy egy másik API-hívás módosítása:
    # weather_data = get_weather_data(city, lat, lon)

    return redirect('/')

@app.route('/railsense', methods=['GET', 'POST'])
def index():
    lat = session.get('lat', 47.046356)
    lon = session.get('lon', 18.057539)
    address = session.get('address', "Balatonfűzfő")
    radius = session.get('radius', 2000)
    
    # Például adjunk hozzá néhány értéket a session-hoz
    session['lat'] = lat
    session['lon'] = lon
    session['radius'] = radius
    session['address'] = address

    manifest_url = url_for('static', filename='manifest.json')

    print(lat, lon, radius, address)
    
    # Fetch train data
    arrivals_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon={lon}&clientLat={lat}&onlyDepartures=false&limit=60&lat={lat}&lon={lon}&radius={radius}&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"

    arrivals_response = requests.get(arrivals_url)
    
    trainsdata = []
    added_trains = set()  # This stores trains that have already been added
    result_status = 2  # Default value: no train
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
                text_color = route_info.get('textColor', 'FFFFFF')
            else:
                short_name = "N/A"
                description = "N/A"
                
            for stop_time in stop_times:
                train_id = stop_time['tripId']
                if train_id not in added_trains:
                    if 'arrivalTime' in stop_time:
                        arrival_time = datetime.datetime.fromtimestamp(stop_time['arrivalTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        arrival_time = datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M')

                    if 'departureTime' in stop_time:
                        departure_time = datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        departure_time = datetime.datetime.fromtimestamp(0000000, tz=hungary_tz).strftime('%H:%M')
                    
                    predicted_arrival_time = None
                    if 'predictedArrivalTime' in stop_time:
                        predicted_arrival_time = datetime.datetime.fromtimestamp(stop_time['predictedArrivalTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        predicted_arrival_time = arrival_time
                    
                    # Second API call
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
                                'arrival_time': datetime.datetime.fromtimestamp(stop['arrivalTime'], tz=hungary_tz).strftime('%H:%M') if 'arrivalTime' in stop else datetime.datetime.fromtimestamp(stop['departureTime'], tz=hungary_tz).strftime('%H:%M'),
                                'departure_time': datetime.datetime.fromtimestamp(stop['departureTime'], tz=hungary_tz).strftime('%H:%M') if 'departureTime' in stop else 'N/A',
                                'predicted_arrival_time': datetime.datetime.fromtimestamp(stop['predictedArrivalTime'], tz=hungary_tz).strftime('%H:%M') if 'predictedArrivalTime' in stop else 'N/A',
                                'predicted_departure_time': datetime.datetime.fromtimestamp(stop['predictedDepartureTime'], tz=hungary_tz).strftime('%H:%M') if 'predictedDepartureTime' in stop else 'N/A'
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
                        'text_color': text_color,
                        'trip_details': trip_details # Add second API response
                    })
                    added_trains.add(train_id)
                    result_status = 1  # Train detected
        try:
            # Ellenőrizd, hogy a trainsdata lista megfelelő adatokat tartalmaz-e
            if all('predicted_arrival_time' in train for train in trainsdata):
                # Rendezd a trainsdata listát a 'predicted_arrival_time' alapján
                sorted_trainsdata = sorted(trainsdata, key=lambda x: datetime.datetime.strptime(x['predicted_arrival_time'], '%H:%M'))
            else:
                # Ha az adatok nem megfelelőek, kezeld a hibát vagy hagyd ki a rendezést
                sorted_trainsdata = trainsdata
        except Exception as e:
            # Kezeld a kivételt, ha szükséges
            sorted_trainsdata = []

    elif arrivals_response.status_code != 200:
        message = "404 Error on the page"
        result_status = 3
    
    # Fetch weather data
    city = "Balatonfuzfo"
    weather_data = get_weather_data(city)

    return render_template('index.html', trainsdata=trainsdata, result_status=result_status, manifest_url=manifest_url, message=message, weather_data=weather_data, address = address)

@app.errorhandler(requests.exceptions.ConnectionError)
def handle_connection_error(error):
    return render_template('connection_error.html'), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)