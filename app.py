from flask import Flask, render_template, request, url_for, session, redirect
import requests
import datetime
import pytz
from bs4 import BeautifulSoup

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

@app.route('/fullscreen_map')
def search():
    lat = session.get('lat', 47.046356)
    lon = session.get('lon', 18.057539)

    return render_template('maps.html', lat = lat, lon = lon)

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
    return redirect('/')



@app.route('/')
def fullscreen_map():
    # Az URL, ahonnan le kell kérni a HTML tartalmat
    # A railsense route hívása
    railsense_html = index()  # A railsense() funkció helyi hívása

    # A BeautifulSoup használata a HTML kinyeréséhez
    soup = BeautifulSoup(railsense_html, 'html.parser')
    card_div = soup.find('div', {'class': 'card', 'style': 'max-width: 30rem;'})

    # Ellenőrzés, hogy megtaláltuk-e a kért divet
    if card_div:
        card_html = card_div.prettify()  # A kinyert HTML
    else:
        card_html = '''
                        




<div class="card" style="max-width: 30rem;">
                        <div style="padding: 0px; overflow: hidden;" class="card-header">
                            <div style="float: left; padding: 13px;">
                                <p id="description" class="card-title text-light description">Nincs semmi a láthatáron</p>
                                <h4 id="headsign" class="card-subtitle headsign" style="margin-bottom: 0px; margin-top: 5px; color: #3FC555">Szabadon átkelhet</h4>
                            </div>
                            <div class="viszonylatdoboz d-flex justify-content-center align-items-center" style="float: right; padding: 10px; border-top-right-radius: 5px; background-color: #3FC555 !important; width: 90px; height: 85px;">
                                <span class="shortname" style=" font-weight: bolder ;color: #3C3C3C;">✔️</span>
                            </div>
                            <script>
                                document.addEventListener('DOMContentLoaded', function () {
                                    function applyMarquee(element) {
                                        if (element.scrollWidth > element.clientWidth) {
                                            var container = document.createElement('div');
                                            container.className = 'marquee-container';
                                            var marquee = document.createElement('div');
                                            marquee.className = 'marquee';
                                            marquee.innerHTML = element.innerHTML;
                                            container.appendChild(marquee);
                                            element.innerHTML = '';
                                            element.appendChild(container);
                                        }
                                    }

                                    var description = document.getElementById('description');
                                    var headsign = document.getElementById('headsign');

                                    applyMarquee(description);
                                    applyMarquee(headsign);
                                });
                            </script>

                        </div>
                        <div class="card-body text-light"
                            style="border-bottom: var(--bs-card-border-width) solid var();">

                            <div class="accordion accordion" id="accordionExample">
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button"
                                            data-bs-toggle="collapse" data-bs-target="#collapse{{ loop.index }}"
                                            aria-expanded="false" aria-controls="collapse{{ loop.index }}"
                                            data-index="{{ loop.index }}">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="26" height="23" viewBox="0 0 26 23" fill="none">
                                                <g clip-path="url(#clip0_122_60)">
                                                <path d="M3.79883 22.9785H21.2109C23.7402 22.9785 25.0195 21.709 25.0195 19.2188V3.78906C25.0195 1.29883 23.7402 0.0292969 21.2109 0.0292969H3.79883C1.2793 0.0292969 0 1.28906 0 3.78906V19.2188C0 21.7188 1.2793 22.9785 3.79883 22.9785ZM3.66211 21.25C2.41211 21.25 1.72852 20.5859 1.72852 19.2969V7.64648C1.72852 6.34766 2.41211 5.69336 3.66211 5.69336H21.3379C22.5781 5.69336 23.2812 6.34766 23.2812 7.64648V19.2969C23.2812 20.5859 22.5781 21.25 21.3379 21.25H3.66211ZM10.0195 10.1855H10.7617C11.1816 10.1855 11.2988 10.0684 11.2988 9.6582V8.92578C11.2988 8.51562 11.1816 8.4082 10.7617 8.4082H10.0195C9.60938 8.4082 9.49219 8.51562 9.49219 8.92578V9.6582C9.49219 10.0684 9.60938 10.1855 10.0195 10.1855ZM14.2676 10.1855H15.0098C15.4199 10.1855 15.5371 10.0684 15.5371 9.6582V8.92578C15.5371 8.51562 15.4199 8.4082 15.0098 8.4082H14.2676C13.8477 8.4082 13.7305 8.51562 13.7305 8.92578V9.6582C13.7305 10.0684 13.8477 10.1855 14.2676 10.1855ZM18.5059 10.1855H19.248C19.6582 10.1855 19.7852 10.0684 19.7852 9.6582V8.92578C19.7852 8.51562 19.6582 8.4082 19.248 8.4082H18.5059C18.0957 8.4082 17.9688 8.51562 17.9688 8.92578V9.6582C17.9688 10.0684 18.0957 10.1855 18.5059 10.1855ZM5.78125 14.3555H6.52344C6.93359 14.3555 7.06055 14.248 7.06055 13.8379V13.0957C7.06055 12.6953 6.93359 12.5781 6.52344 12.5781H5.78125C5.37109 12.5781 5.24414 12.6953 5.24414 13.0957V13.8379C5.24414 14.248 5.37109 14.3555 5.78125 14.3555ZM10.0195 14.3555H10.7617C11.1816 14.3555 11.2988 14.248 11.2988 13.8379V13.0957C11.2988 12.6953 11.1816 12.5781 10.7617 12.5781H10.0195C9.60938 12.5781 9.49219 12.6953 9.49219 13.0957V13.8379C9.49219 14.248 9.60938 14.3555 10.0195 14.3555ZM14.2676 14.3555H15.0098C15.4199 14.3555 15.5371 14.248 15.5371 13.8379V13.0957C15.5371 12.6953 15.4199 12.5781 15.0098 12.5781H14.2676C13.8477 12.5781 13.7305 12.6953 13.7305 13.0957V13.8379C13.7305 14.248 13.8477 14.3555 14.2676 14.3555ZM18.5059 14.3555H19.248C19.6582 14.3555 19.7852 14.248 19.7852 13.8379V13.0957C19.7852 12.6953 19.6582 12.5781 19.248 12.5781H18.5059C18.0957 12.5781 17.9688 12.6953 17.9688 13.0957V13.8379C17.9688 14.248 18.0957 14.3555 18.5059 14.3555ZM5.78125 18.5352H6.52344C6.93359 18.5352 7.06055 18.4277 7.06055 18.0176V17.2754C7.06055 16.8652 6.93359 16.7578 6.52344 16.7578H5.78125C5.37109 16.7578 5.24414 16.8652 5.24414 17.2754V18.0176C5.24414 18.4277 5.37109 18.5352 5.78125 18.5352ZM10.0195 18.5352H10.7617C11.1816 18.5352 11.2988 18.4277 11.2988 18.0176V17.2754C11.2988 16.8652 11.1816 16.7578 10.7617 16.7578H10.0195C9.60938 16.7578 9.49219 16.8652 9.49219 17.2754V18.0176C9.49219 18.4277 9.60938 18.5352 10.0195 18.5352ZM14.2676 18.5352H15.0098C15.4199 18.5352 15.5371 18.4277 15.5371 18.0176V17.2754C15.5371 16.8652 15.4199 16.7578 15.0098 16.7578H14.2676C13.8477 16.7578 13.7305 16.8652 13.7305 17.2754V18.0176C13.7305 18.4277 13.8477 18.5352 14.2676 18.5352Z" fill="#C6C6C6"/>
                                                </g>
                                                <defs>
                                                <clipPath id="clip0_122_60">
                                                <rect width="25.3809" height="22.9785" fill="white"/>
                                                </clipPath>
                                                </defs>
                                                </svg>
                                                <span style="padding-left: 10px !important;">Menetrend (hamarosan)</span>
                                            

                                        </button>
                                    </h2>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer" style="background-color: var(--primary-color); vertical-align: top;">
                            <div class="rounded" style="padding: 5px; vertical-align: middle; width: fit-content; border: 1px solid;">
                                <div style="vertical-align: middle; box-sizing: border-box; display: flex; flex-direction: row;">
                                    
                                    <svg class="svgtime" style="box-sizing: border-box; overflow: scroll; background-color: transparent;" width="22" height="22" viewBox="0 0 22 19" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M9.0791 18.7334C10.292 18.7334 11.4697 18.4873 12.5508 18.0303C12.1377 17.582 11.8213 17.0547 11.5928 16.4922C10.8105 16.7822 9.9668 16.9492 9.0791 16.9492C5.03613 16.9492 1.79297 13.6973 1.79297 9.6543C1.79297 5.61133 5.02734 2.36816 9.07031 2.36816C12.7266 2.36816 15.7412 5.04004 16.2686 8.54688C16.8135 8.45898 17.5342 8.48535 18.0879 8.62598C17.5693 4.12598 13.6934 0.575195 9.07031 0.575195C4.0957 0.575195 0 4.68848 0 9.6543C0 14.6289 4.10449 18.7334 9.0791 18.7334ZM4.63184 10.7441H9.07031C9.46582 10.7441 9.76465 10.4365 9.76465 10.0498V4.28418C9.76465 3.89746 9.46582 3.58984 9.07031 3.58984C8.68359 3.58984 8.37598 3.89746 8.37598 4.28418V9.35547H4.63184C4.23633 9.35547 3.9375 9.6543 3.9375 10.0498C3.9375 10.4365 4.23633 10.7441 4.63184 10.7441ZM16.875 18.7773C19.3359 18.7773 21.4014 16.7207 21.4014 14.251C21.4014 11.7725 19.3535 9.7334 16.875 9.7334C14.3965 9.7334 12.3486 11.7725 12.3486 14.251C12.3486 16.7383 14.3965 18.7773 16.875 18.7773ZM16.3477 16.9229C16.1807 16.9229 15.9785 16.8525 15.8467 16.7119L14.1943 14.9014C14.1064 14.8135 14.0449 14.6377 14.0449 14.4883C14.0449 14.1104 14.335 13.8643 14.6689 13.8643C14.8711 13.8643 15.0293 13.9434 15.1436 14.0664L16.3125 15.3496L18.5537 12.2295C18.6768 12.0713 18.8613 11.957 19.0811 11.957C19.4238 11.957 19.7139 12.2295 19.7139 12.5811C19.7139 12.6865 19.6699 12.8271 19.582 12.9414L16.8662 16.6855C16.7607 16.8262 16.5586 16.9229 16.3477 16.9229Z"></path>
                                    </svg>
                                    <span style="padding-left: 5px !important;"> Most frissítve</span>
                                </div>
                            </div>
                        </div>
                    </div>
'''

    # Sessionből további adatok
    lat = session.get('lat', 47.046356)
    lon = session.get('lon', 18.057539)
    address = session.get('address', "Balatonfűzfő")
    manifest_url = url_for('static', filename='manifest.json')

    # Az adatokat a HTML sablonnak adjuk át
    return render_template('fullscreen_map.html', lat=lat, lon=lon, address=address, manifest_url=manifest_url, card_html=card_html)


@app.route('/railsense', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get latitude and longitude from POST request
        data = request.get_json()
        lat = data.get('lat', 47.046356)  # Default value if not provided
        lon = data.get('lon', 18.057539)  # Default value if not provided

        # Save the data in session
        session['lat'] = lat
        session['lon'] = lon

        return jsonify({'status': 'success', 'lat': lat, 'lon': lon})

    # Default values for GET request
    lat = session.get('lat', 47.046356)
    lon = session.get('lon', 18.057539)
    address = session.get('address', "Balatonfűzfő")
    radius = session.get('radius', 2000)

    # Update session
    session['lat'] = lat
    session['lon'] = lon
    session['radius'] = radius
    session['address'] = address


    manifest_url = url_for('static', filename='manifest.json')

    arrivals_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon={lon}&clientLat={lat}&onlyDepartures=false&limit=60&lat={lat}&lon={lon}&radius={radius}&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&minutesAfter=30&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
    vehicles_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/vehicles-for-location?&clientLon={lon}&clientLat={lat}&onlyDepartures=false&limit=60&lat={lat}&lon={lon}&radius={radius}&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&minutesAfter=60&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
    
    arrivals_response = requests.get(arrivals_url)
    vehicles_response = requests.get(vehicles_url)
    
    trainsdata = []
    added_trains = set()  
    result_status = 2  
    message = ""

    if arrivals_response.status_code == 200 and vehicles_response.status_code == 200:
        arrivals_data = arrivals_response.json()['data']['list']
        vehicles_data = vehicles_response.json()['data']['list']
        
        """ # Print vehicles_data to check its structure
        print(vehicles_data) """
        
        routes_data = arrivals_response.json()['data']['references']['routes']
        
        for item in arrivals_data:
            route_id = item['routeId']
            headsign = item['headsign']
            stop_times = item['stopTimes']
           
            if route_id in routes_data:
                route_info = routes_data[route_id]
                short_name = route_info.get('shortName', 'N/A')
                description = route_info.get('description', 'N/A')
                type = route_info.get('type', 'N/A')
                color = route_info.get('color', 'N/A')
                text_color = route_info.get('textColor', 'FFFFFF')
            else:
                short_name = "N/A"
                description = "N/A"
                type = "N/A"
                
            for stop_time in stop_times:
                train_id = stop_time['tripId']
                if train_id not in added_trains and (type == 'RAIL' or type == "N/A"):
                    if 'arrivalTime' in stop_time:
                        arrival_time = datetime.datetime.fromtimestamp(stop_time['arrivalTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        arrival_time = datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M')

                    if 'departureTime' in stop_time:
                        departure_time = datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        departure_time = 'N/A'
                    
                    predicted_arrival_time = None
                    if 'predictedArrivalTime' in stop_time:
                        predicted_arrival_time = datetime.datetime.fromtimestamp(stop_time['predictedArrivalTime'], tz=hungary_tz).strftime('%H:%M')
                    else:
                        predicted_arrival_time = arrival_time
                    
                    trip_details_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/trip-details?tripId={train_id}&version=4&includeReferences=stops&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
                    trip_details_response = requests.get(trip_details_url)
                    
                    trip_details = []
                    vehicle_name = 'N/A'
                    vehicle_label = 'N/A'
                    if trip_details_response.status_code == 200:
                        trip_details_data = trip_details_response.json()['data']['entry']['stopTimes']
                        
                        stops_data = trip_details_response.json()['data']['references']['stops']
                        vehicle = trip_details_response.json()['data']['entry'].get('vehicle', {})
                        
                        vehicle_name = vehicle.get('style', {}).get('icon', {}).get('name', '')
                        vehicletype = vehicle.get('style', {}).get('vehicleIcon', {}).get('name', 'RAIL')
                        vehicle_label = vehicle.get('model', '')
                        stop_sequence = vehicle.get('stopSequence')

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
                                'predicted_departure_time': datetime.datetime.fromtimestamp(stop['predictedDepartureTime'], tz=hungary_tz).strftime('%H:%M') if 'predictedDepartureTime' in stop else 'N/A',
                                'stopseqe2': stop.get('stopSequence')
                            })
                    
                    # Find vehicle coordinates
                    vehicle_data = next((v for v in vehicles_data if v.get('tripId') == train_id), {})
                    vehicle_lat = vehicle_data.get('lat', 'N/A')
                    vehicle_lon = vehicle_data.get('lon', 'N/A')

                    trainsdata.append({
                        'route_id': route_id,
                        'headsign': headsign,
                        'stop_id': stop_time['stopId'],
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'predicted_arrival_time': predicted_arrival_time,
                        'short_name': short_name,
                        'description': description,
                        'stop_sequence': stop_sequence,
                        'type': type,
                        'color': color,
                        'text_color': text_color,
                        'vehicle_name': vehicle_name,
                        'vehicle_label': vehicle_label,
                        'vehicletype': vehicletype,
                        'trip_details': trip_details,
                        'vehicle_lat': vehicle_lat,
                        'vehicle_lon': vehicle_lon
                    })
                    added_trains.add(train_id)
                    result_status = 1  
        
        try:
            if all('predicted_arrival_time' in train for train in trainsdata):
                sorted_trainsdata = sorted(trainsdata, key=lambda x: datetime.datetime.strptime(x['predicted_arrival_time'], '%H:%M'))
            else:
                sorted_trainsdata = trainsdata
        except Exception as e:
            sorted_trainsdata = []

    else:
        message = "Error fetching data from the APIs"
        result_status = 3
    
    city = "Balatonfuzfo"
    weather_data = get_weather_data(city)

    return render_template('index.html', trainsdata=sorted_trainsdata, result_status=result_status, manifest_url=manifest_url, message=message, weather_data=weather_data, address=address)

@app.errorhandler(requests.exceptions.ConnectionError)
def handle_connection_error(error):
    return render_template('connection_error.html'), 500

if __name__ == '__main__':
    app.run( port=10000, debug=True)
