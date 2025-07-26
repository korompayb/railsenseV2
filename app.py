from flask import Flask, render_template, request, url_for, session, redirect
import requests
import datetime
import pytz
from bs4 import BeautifulSoup
import json


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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/connection_error')
def connection_error():
    return render_template('connection_error.html')

@app.route('/')
def fullscreen_map():
    # Get HTML content from railsense route
    railsense_html = index()
    soup = BeautifulSoup(railsense_html, 'html.parser')
    card_div = soup.find('div', {'class': 'card', 'style': 'max-width: 30rem;'})

    # Initialize variables with default "no train" values
    description = "Nincs vonat a közelben"
    headsign = "Szabad az átkelés "
    arrival_time = "A közeljövőben nem várható vonat"
    color = "#3FC555"  # Default green color
    short_name = '<i class="fa-solid fa-check"></i>'
    accordion_html = ""

    # Only try to scrape if card_div exists
    if card_div:
        accordion_bodies = soup.find_all('div', class_='accordion-body')
        
        # Create accordion_html for each train's schedule
        if accordion_bodies:
            first_accordion = accordion_bodies[0]
            schedule_table = first_accordion.find('table', id='menetrend')
            if schedule_table:
                accordion_html = str(schedule_table)

        # Try to find first train data
        train = soup.find('div', class_='card')
        if train:
            desc_elem = train.find('p', class_='description')
            head_elem = train.find('h4', class_='headsign')
            color_elem = train.find('div', class_='viszonylatdoboz')
            short_name_elem = train.find('span', class_='shortname')
            arrival_time_span = train.find('span', class_='erkezik')

            if desc_elem:
                description = desc_elem.text.strip()
            if head_elem:
                headsign = head_elem.text.strip()
            if color_elem and 'style' in color_elem.attrs:
                style = color_elem['style']
                if 'background-color:#' in style:
                    color = '#' + style.split('background-color:#')[1].split()[0]
            if short_name_elem:
                short_name = short_name_elem.text.strip()
            if arrival_time_span:
                arrival_time = arrival_time_span.text.strip()

    
    # Get session data
    lat = session.get('lat', 47.046356)
    lon = session.get('lon', 18.057539)
    address = session.get('address', "Balatonfűzfő")
    manifest_url = url_for('static', filename='manifest.json')

    return render_template('fullscreen_map.html', lat=lat, lon=lon, address=address, 
                         manifest_url=manifest_url, 
                         headsign=headsign, description=description, 
                         arrival_time=arrival_time, color=color, 
                         short_name=short_name, accordion_html=accordion_html)


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
    print(f"Arrivals URL: {vehicles_url}")
    offline_arrivals_url = "static/menetrend_balatonfuzfo.json"
    
    arrivals_response = None
    vehicles_response = None
    
    # Próbáljuk meg lekérni az online adatokat
    try:
        arrivals_response = requests.get(arrivals_url, timeout=5)
        vehicles_response = requests.get(vehicles_url, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Hiba az online API hívásakor: {e}")
        # result_status és message kezelése később, az offline betöltés után

    trainsdata = []
    added_trains = set() # Trip ID-k tárolására
    result_status = 2
    message = ""

    # Online adatok feldolgozása
    if arrivals_response and arrivals_response.status_code == 200 and \
       vehicles_response and vehicles_response.status_code == 200:
        try:
            arrivals_data = arrivals_response.json()['data']['list']
            vehicles_data = vehicles_response.json()['data']['list']
            routes_data = arrivals_response.json()['data']['references']['routes']

            for item in arrivals_data:
                route_id = item['routeId']
                headsign = item['headsign']
                stop_times = item['stopTimes']

                route_info = routes_data.get(route_id, {})
                short_name = route_info.get('shortName', 'N/A')
                description = route_info.get('description', 'N/A')
                type = route_info.get('type', 'N/A')
                color = route_info.get('color', 'N/A')
                text_color = route_info.get('textColor', 'FFFFFF')
                    
                for stop_time in stop_times:
                    train_id = stop_time['tripId'] # Online adatoknál van tripId
                    
                    if train_id not in added_trains and (type == 'RAIL' or type == "COACH"):
                        # Időpontok konvertálása
                        arrival_time = datetime.datetime.fromtimestamp(stop_time.get('arrivalTime', stop_time.get('departureTime')), tz=hungary_tz).strftime('%H:%M')
                        departure_time = datetime.datetime.fromtimestamp(stop_time['departureTime'], tz=hungary_tz).strftime('%H:%M') if 'departureTime' in stop_time else 'N/A'
                        predicted_arrival_time = datetime.datetime.fromtimestamp(stop_time.get('predictedArrivalTime', stop_time.get('arrivalTime', stop_time.get('departureTime'))), tz=hungary_tz).strftime('%H:%M')
                        
                        # Trip details lekérése
                        trip_details_url = f"https://futar.bkk.hu/api/query/v1/ws/otp/api/where/trip-details?tripId={train_id}&version=4&includeReferences=stops&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
                        trip_details_response = requests.get(trip_details_url)
                        
                        trip_details = []
                        vehicle_name = 'N/A'
                        vehicle_label = 'N/A'
                        vehicletype = 'N/A'
                        stop_sequence = 'N/A'
                        
                        if trip_details_response.status_code == 200:
                            trip_details_json = trip_details_response.json()
                            entry = trip_details_json.get('data', {}).get('entry', {})
                            trip_details_data = entry.get('stopTimes', [])
                            stops_data = trip_details_json.get('data', {}).get('references', {}).get('stops', {})
                            vehicle = entry.get('vehicle', {})
                            
                            vehicle_name = vehicle.get('style', {}).get('icon', {}).get('name', '')
                            vehicletype = vehicle.get('style', {}).get('vehicleIcon', {}).get('name', 'RAIL')
                            vehicle_label = vehicle.get('model', '')
                            stop_sequence = vehicle.get('stopSequence', 'N/A')
                            
                            for stop in trip_details_data:
                                stop_id_detail = stop['stopId'] # Átnevezve, hogy ne ütközzön
                                stop_info = stops_data.get(stop_id_detail, {})
                                trip_details.append({
                                    'stop_id': stop_id_detail,
                                    'stop_name': stop_info.get('name', 'N/A'),
                                    'stop_lat': stop_info.get('lat', 'N/A'),
                                    'stop_lon': stop_info.get('lon', 'N/A'),
                                    'arrival_time': datetime.datetime.fromtimestamp(stop.get('arrivalTime', stop.get('departureTime')), tz=hungary_tz).strftime('%H:%M'),
                                    'departure_time': datetime.datetime.fromtimestamp(stop['departureTime'], tz=hungary_tz).strftime('%H:%M') if 'departureTime' in stop else 'N/A',
                                    'predicted_arrival_time': datetime.datetime.fromtimestamp(stop.get('predictedArrivalTime', stop.get('arrivalTime', stop.get('departureTime'))), tz=hungary_tz).strftime('%H:%M'),
                                    'predicted_departure_time': datetime.datetime.fromtimestamp(stop.get('predictedDepartureTime', stop.get('departureTime', 0)), tz=hungary_tz).strftime('%H:%M') if stop.get('predictedDepartureTime') else 'N/A',
                                    'stopseqe2': stop.get('stopSequence')
                                })
                        
                        # Jármű koordináták
                        vehicle_data = next((v for v in vehicles_data if v.get('tripId') == train_id), {})
                        vehicle_lat = vehicle_data.get('lat', 'N/A')
                        vehicle_lon = vehicle_data.get('lon', 'N/A')

                        # Percek számítása
                        now = datetime.datetime.now(tz=hungary_tz)
                        predicted_arrival_dt = datetime.datetime.fromtimestamp(stop_time.get('predictedArrivalTime', stop_time.get('arrivalTime', stop_time.get('departureTime'))), tz=hungary_tz)
                        predicted_arrival_minutes = int((predicted_arrival_dt - now).total_seconds() // 60)
                        if predicted_arrival_minutes > 0:
                            predicted_arrival_minutes_text = f"{predicted_arrival_minutes} perc múlva érkezik"
                        elif predicted_arrival_minutes == 0:
                            predicted_arrival_minutes_text = "Most érkezik"
                        else:
                            predicted_arrival_minutes_text = "Már elment"

                        trainsdata.append({
                            'route_id': route_id,
                            'headsign': headsign,
                            'stop_id': stop_time['stopId'],
                            'arrival_time': arrival_time,
                            'departure_time': departure_time,
                            'predicted_arrival_time': predicted_arrival_time,
                            'predicted_departure_time': stop_time.get('predictedDepartureTime', 'N/A'),
                            'predicted_arrival_minutes': predicted_arrival_minutes_text,
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
                            'vehicle_lon': vehicle_lon,
                            'source': 'online' # Forrás azonosítása
                        })
                        added_trains.add(train_id)
            result_status = 1 # Online adatok sikeresen betöltve
        except Exception as e:
            message = f"Hiba az online adatok feldolgozásakor: {e}"
            result_status = 3
    else:
        message = "Hiba az online API-k elérésében vagy feldolgozásában."
        result_status = 3 # Online adatok nem elérhetők/hibásak

    # --- Offline adatok betöltése és hozzáadása ---
    try:
        with open(offline_arrivals_url, 'r', encoding='utf-8') as f:
            offline_list_data = json.load(f) # A JSON fájl egy lista
            
            for item in offline_list_data:
                current_trip_id = None
                if 'stopTimes' in item and item['stopTimes']:
                    current_trip_id = item['stopTimes'][0].get('tripId') # Megpróbáljuk kinyerni
                
                if current_trip_id is None:
                    # Ha nincs tripId, generálunk egy egyedit
                    # Fontos: egyedi ID-t kell generálni, ami nem ütközik az online-nal vagy más offline-nal
                    # Itt most egy időpecsétet adok hozzá a routeId és headsign mellé, hogy egyedibb legyen.
                    current_trip_id = f"OFFLINE_{item.get('routeId', 'UNKNOWN')}_{item.get('headsign', 'N/A')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                
                if current_trip_id not in added_trains:
                    route_id = item.get('routeId', 'OFFLINE')
                    headsign = item.get('headsign', 'Offline járat')
                    
                    for stop_time in item.get('stopTimes', []):
                        now = datetime.datetime.now(tz=hungary_tz)

                        arrival_time_str = stop_time.get('arrivalTime', None)
                        # Megjegyzés: a departure_timestamp is hasznos lehet, de csak ha valódi időbélyeg
                        # Jelenleg a 'departureTime' kulcsot használja, ami feltételezi, hogy az is 'HH:MM' string
                        departure_time_str = stop_time.get('departureTime', None) 
                        predicted_arrival_time_str = stop_time.get('predictedArrivalTime', None)

                        # Csak az órát és percet vesszük figyelembe, dátum nélkül (általános menetrend)
                        arrival_dt = now
                        if arrival_time_str:
                            try:
                                arrival_hour, arrival_minute = map(int, arrival_time_str.split(':'))
                                # Kiszámoljuk, hogy hány perc van még az érkezésig (csak óra:perc alapján, dátum nélkül)
                                now_minutes = now.hour * 60 + now.minute
                                arrival_minutes = arrival_hour * 60 + arrival_minute
                                time_until_arrival_minutes = arrival_minutes - now_minutes
                                if time_until_arrival_minutes < 0:
                                    time_until_arrival_minutes += 24 * 60  # Másnapra tolódik
                                # arrival_dt csak az időpontot tartalmazza, a mai napra
                                arrival_dt = now.replace(hour=arrival_hour, minute=arrival_minute, second=0, microsecond=0)
                                if arrival_dt < now:
                                    arrival_dt += datetime.timedelta(days=1)
                            except ValueError:
                                print(f"Hiba: Érvénytelen offline arrivalTime formátum ('{arrival_time_str}'). Elvárás: HH:MM")
                                continue # Folytatjuk a következő stop_time-al, ha ez hibás
                        else:
                            # Ha nincs megadva érkezési idő, kihagyjuk ezt a stop_time-ot
                            continue

                        departure_dt = None
                        if departure_time_str:
                            try:
                                departure_dt = datetime.datetime.strptime(departure_time_str, '%H:%M').replace(
                                    year=now.year, month=now.month, day=now.day, tzinfo=hungary_tz)
                                if departure_dt < now:
                                    departure_dt += datetime.timedelta(days=1)
                            except ValueError:
                                print(f"Hiba: Érvénytelen offline departureTime formátum ('{departure_time_str}'). Elvárás: HH:MM")
                                pass # Hiba esetén a departure_dt None marad

                        predicted_arrival_dt = arrival_dt
                        if predicted_arrival_time_str:
                            try:
                                predicted_arrival_dt = datetime.datetime.strptime(predicted_arrival_time_str, '%H:%M').replace(
                                    year=now.year, month=now.month, day=now.day, tzinfo=hungary_tz)
                                if predicted_arrival_dt < now:
                                    predicted_arrival_dt += datetime.timedelta(days=1)
                            except ValueError:
                                print(f"Hiba: Érvénytelen offline predictedArrivalTime formátum ('{predicted_arrival_time_str}'). Elvárás: HH:MM")
                                pass # Hiba esetén a predicted_arrival_dt az arrival_dt értéke marad

                        # --- Az új feltétel: csak ha a következő 60 percen belül van ---
                        time_until_arrival_minutes = int((predicted_arrival_dt - now).total_seconds() // 60)
                        
                        # Fontos: Csak akkor adjuk hozzá, ha az idő a jövőben van ÉS 60 percen belül van
                        if 0 <= time_until_arrival_minutes <= 20:
                            predicted_arrival_minutes_text = f"{time_until_arrival_minutes} perc múlva érkezik"
                            if time_until_arrival_minutes == 0:
                                predicted_arrival_minutes_text = "Most érkezik"

                            trainsdata.append({
                                'route_id': route_id,
                                'headsign': headsign,
                                'stop_id': stop_time.get('stopId', 'N/A'),
                                'arrival_time': arrival_dt.strftime('%H:%M'),
                                'departure_time': departure_dt.strftime('%H:%M') if departure_dt else 'N/A', # Használjuk a konvertált departure_dt-t
                                'predicted_arrival_time': predicted_arrival_dt.strftime('%H:%M'),
                                'predicted_departure_time': stop_time.get('predictedDepartureTime', 'N/A'), # Ha az offline JSON-ban is stringként van
                                'predicted_arrival_minutes': predicted_arrival_minutes_text,
                                'short_name': item.get('shortName', 'Offline'),
                                'description': item.get('description', 'Offline menetrend'),
                                'stop_sequence': stop_time.get('stopSequence', 'N/A'),
                                'type': item.get('type', 'RAIL'), # Feltételezzük, hogy offline is lehet RAIL
                                'color': item.get('color', '808080'),
                                'text_color': item.get('textColor', 'FFFFFF'),
                                'vehicle_name': item.get('vehicleName', 'N/A'),
                                'vehicle_label': item.get('vehicleLabel', 'N/A'),
                                'vehicletype': item.get('vehicletype', 'RAIL'), # Feltételezzük, hogy offline is lehet RAIL
                                'trip_details': item.get('tripDetails', []),
                                'vehicle_lat': item.get('vehicleLat', 'N/A'),
                                'vehicle_lon': item.get('vehicleLon', 'N/A'),
                                'source': 'offline'
                            })
                            added_trains.add(current_trip_id) # Hozzáadjuk a generált ID-t, miután hozzáadtuk a vonatot
                        else:
                            # print(f"Offline vonat ({headsign} - {predicted_arrival_dt.strftime('%H:%M')}) kihagyva, mert nem 60 percen belül érkezik.")
                            pass # Nem adjuk hozzá, ha nem esik bele az 1 órás intervallumba

            # Ha az online hívás sikertelen volt, de az offline adatok betöltődtek, akkor is OK
            if result_status == 3 and trainsdata: # Ha az online API hibázott, de offline-ból van adat
                result_status = 1
                message = "Adatok betöltve (részben offline forrásból)."
            elif not trainsdata and result_status == 3: # Ha online és offline is hibás
                message = "Sem online, sem offline adatok nem tölthetők be."

    except FileNotFoundError:
        print(f"Hiba: Az offline adatfájl ({offline_arrivals_url}) nem található.")
        if not trainsdata: # Ha az online és az offline is hibás
            result_status = 3
            message = "Sem online, sem offline adatok nem tölthetők be."
    except json.JSONDecodeError:
        print(f"Hiba: Az offline adatfájl ({offline_arrivals_url}) hibás JSON formátumú.")
        if not trainsdata:
            result_status = 3
            message = "Hibás offline adatfájl."
    except Exception as e:
        print(f"Ismeretlen hiba az offline adatok betöltésekor: {e}")
        if not trainsdata:
            result_status = 3
            message = f"Hiba az offline adatok feldolgozásakor: {e}"

    # Rendezés a predicted_arrival_time alapján
    try:
        # Konvertáljuk az időpontokat datetime objektumokká a rendezéshez
        # Ha predicted_arrival_time "N/A", akkor tegyük a lista végére
        
        # Először szűrjük azokat, amiknek van érvényes ideje
        sortable_trains = [t for t in trainsdata if t.get('predicted_arrival_time') and t['predicted_arrival_time'] != 'N/A']
        
        # Rendezés a 'HH:MM' string alapján, ami kronológiailag helyes lesz
        sorted_trainsdata = sorted(sortable_trains, key=lambda x: datetime.datetime.strptime(x['predicted_arrival_time'], '%H:%M'))
        
        # Végül adjuk hozzá azokat, amiknek nincs ideje (vagy 'N/A'), a lista végére
        unsortable_trains = [t for t in trainsdata if not t.get('predicted_arrival_time') or t['predicted_arrival_time'] == 'N/A']
        sorted_trainsdata.extend(unsortable_trains)

    except Exception as e:
        print(f"Hiba a rendezés során: {e}")
        sorted_trainsdata = trainsdata # Hiba esetén rendezetlenül hagyjuk

    city = "Balatonfuzfo"
    weather_data = get_weather_data(city)

    return render_template('index.html', trainsdata=sorted_trainsdata, result_status=result_status, manifest_url=manifest_url, message=message, weather_data=weather_data, address=address)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_connection_error(error):
    return render_template('connection_error.html'), 500

if __name__ == '__main__':
    app.run( port=10000, debug=True)
