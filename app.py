from flask import Flask, render_template, request, url_for
from datetime import datetime
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    manifest_url = url_for('static', filename='manifest.json')
    url = "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-location?&clientLon=18.057539&clientLat=47.046356&minutesBefore=10&minutesAfter=30&stopId=BKK_005504358_0&includeRouteId=BKK_VP06%2CBKK_0090&onlyDepartures=false&limit=60&lat=47.046356&lon=18.057539&radius=3000&minResult=1&appVersion=1.1.abc&version=2&includeReferences=true&key=7ff7c954-05d3-4dd2-93b6-cb714dcdca69"
    response = requests.get(url)
    trainsdata = []

    if response.status_code == 200:
        response.encoding = 'utf-8'
        data = response.json()       
        data_list = data.get("data", {}).get("list", [])

        if not data_list:  # Check if the list is empty
            return render_template('index.html', manifest_url=manifest_url, result_status=2)
        else:
            trainsdata = []
            items = []
            routes = []
            for item in data_list:
                stop_times = item.get("stopTimes", [])
                headsign = item.get("headsign")
                trainsdata.append(headsign)
                        
                for stop_time in stop_times:
                    predictedArrivalTime = stop_time.get("predictedArrivalTime")
                    if predictedArrivalTime:
                        arrival_time = datetime.fromtimestamp(predictedArrivalTime).strftime('%H:%M')
                    else:
                        arrival_time = "N/A"
                    items.append({
                        'stopId': stop_time.get("stopId"),
                        'stopHeadsign': stop_time.get("stopHeadsign"),
                        'arrivalTime': stop_time.get("arrivalTime"),
                        'departureTime': stop_time.get("departureTime"),
                        'predictedArrivalTime': arrival_time,
                        'predictedDepartureTime': stop_time.get("predictedDepartureTime"),
                        'stopSequence': stop_time.get("stopSequence"),
                        'tripId': stop_time.get("tripId"),
                        'serviceDate': stop_time.get("serviceDate"),
                        'wheelchairAccessible': stop_time.get("wheelchairAccessible"),
                        'mayRequireBooking': stop_time.get("mayRequireBooking"),
                        'alertIds': stop_time.get("alertIds")
                    })
                
                # Retrieve routes data
                routes_data = item.get("routes", {})
                for route_id, route_info in routes_data.items():
                    routes.append({
                        'id': route_info.get("id"),
                        'shortName': route_info.get("shortName"),
                        'description': route_info.get("description"),
                        'type': route_info.get("type"),
                        'color': route_info.get("color"),
                        'textColor': route_info.get("textColor"),
                        'agencyId': route_info.get("agencyId"),
                        'iconDisplayType': route_info.get("iconDisplayType"),
                        'iconDisplayText': route_info.get("iconDisplayText"),
                        'bikesAllowed': route_info.get("bikesAllowed"),
                        'sortOrder': route_info.get("sortOrder")
                    })

            return render_template('index.html', trainsdata=trainsdata, items=items, routes=routes, manifest_url=manifest_url, result_status=1)
    else:
        result_status = 3
        return render_template('index.html', message=f"   Hiba történt a kiszolgálóval való kapcsolodás közben:  {response.status_code}",
                               result_status=result_status, update_time="update_time", manifest_url=manifest_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
