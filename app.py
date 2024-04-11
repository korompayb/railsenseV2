from flask import Flask, render_template, request, url_for
import math
import os
import requests
import smtplib
import time

app = Flask(__name__)

trains = []

current_dir = os.path.dirname(os.path.abspath(__file__))

def update(filename, number):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines[-number:]

def load_trains():
    with open('static/trains.txt', 'a', encoding='utf-8') as f:
        f.write(f'{closest_train};{update_time}\n')

def render_onsite():
    with open('static/trains.txt', 'r', encoding='utf-8') as lines:
        last_five = update('static/trains.txt', 5)
        for line in last_five:
            line = line.strip('\n')
            trains.append(line.split(';'))

def telegram_send(message):
    seconds = time.time()
    token = "YOUR_TELEGRAM_BOT_TOKEN"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    myobj = {'chat_id': 'YOUR_CHAT_ID', 'parse_mode': 'MARKDOWN', 'text': f"{message} \n"}
    x = requests.post(url, json=myobj)

def calculate_time_to_reach_coordinate(start_lat, start_lon, finish_lat, finish_lon, speed):
    lat1 = math.radians(start_lat)
    lon1 = math.radians(start_lon)
    lat2 = math.radians(finish_lat)
    lon2 = math.radians(finish_lon)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  # km
    time = distance / speed  # h
    time_seconds = int(time * 3600)  # h -> mp
    return time_seconds

@app.route('/', methods=['GET', 'POST'])
def index():
    manifest_url = url_for('static', filename='manifest.json')
    with open('static/ek.txt', 'r') as f:
        ek = f.read()
    url = "https://apiv2.oroszi.net/elvira/maps"
    target_lat = 47.046356  # lat,
    target_lon = 18.057539  # long
    max_distance = 2  # km
    speed = 90  # km/h
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        close_trains = []
        for item in data:
            if item.get("company") == "MAV" or item.get("company") == "GYSEV":  # gysev és máv vonatok filterezése
                lat = item.get("lat")
                lon = item.get("lon")
                update_time = item.get("event_time")
                if lat is not None and lon is not None:
                    lat1 = math.radians(target_lat)
                    lon1 = math.radians(target_lon)
                    lat2 = math.radians(lat)
                    lon2 = math.radians(lon)
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    distance = 6371 * c
                    if distance <= max_distance:
                        time_to_reach = calculate_time_to_reach_coordinate(lat, lon, target_lat, target_lon, speed)
                        close_trains.append((item["direction"], time_to_reach))

        if close_trains:
            with open('static/ek.txt', 'r') as f:
                ek = f.read()
                ek = eval(f'{ek} + 0')
                ek += 1
            with open('static/ek.txt', 'w+') as f:
                f.write(str(ek))
            result_status = 1
            closest_train = close_trains[0]
            message = f"{int(closest_train[1])} másodpercen belül."

            print(f"jÖN A VONAT! \n  {closest_train[0]}")
            
            if int(ek) == 1:
                telegram_send(
                    f"*Az átkelés veszélyes!*\n\nSzerelvény érkezik: *{closest_train[0]}* irányban, \n*{closest_train[1]}* másodpercen belül.")
            else:
                pass
            
            return render_template('index.html', message=message, directions=[closest_train[0]], result_status=result_status, update_time=update_time, trains=trains, manifest_url=manifest_url)

        else:
            render_onsite()
            with open('static/ek.txt', 'w+') as f:
                f.write('0')
            result_status = 2
            return render_template('index.html',
                                   message="Óvatosan és magabiztosan közlekedj! Nézz körül minden esetben! ",
                                   result_status=result_status, update_time=update_time, manifest_url=manifest_url)
    else:
        result_status = 3
        return render_template('index.html', message=f"Error occurred: {response.status_code}",
                               result_status=result_status, update_time=update_time, manifest_url=manifest_url)


if __name__ == '__main__':
    render_onsite()
    app.run(host='0.0.0.0', port=81, debug=True)
