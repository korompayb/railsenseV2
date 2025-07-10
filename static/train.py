import json

# Ide másold be a raw_trains listát a JSON-ből (rövidítve vagy teljesen)

raw_trains = [
    {"arrival_time": "00:15", "headsign": "Balatonfüred", "shortname": "S", "description": "BAGOLYVONAT"},
    {"arrival_time": "01:27", "headsign": "Székesfehérvár", "shortname": "S", "description": "BAGOLYVONAT"},
    {"arrival_time": "02:20", "headsign": "Balatonfüred", "shortname": "S", "description": "BAGOLYVONAT"},
    {"arrival_time": "03:27", "headsign": "Budapest-Déli", "shortname": "S", "description": "BAGOLYVONAT"},
    {"arrival_time": "04:13", "headsign": "Balatonfüred", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "05:11", "headsign": "Székesfehérvár", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "05:13", "headsign": "Balatonfüred", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "06:13", "headsign": "Balatonfüred", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "06:26", "headsign": "Székesfehérvár", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "07:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "08:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "08:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "08:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "09:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "09:37", "headsign": "Békéscsaba", "shortname": "Ex", "description": "Csabai Tekergő"},
    {"arrival_time": "10:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "10:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "10:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "11:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "11:37", "headsign": "Záhony", "shortname": "Ex", "description": "Szabolcsi Tekergő"},
    {"arrival_time": "12:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "12:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "12:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "13:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "14:13", "headsign": "Zánka-Erzsébettábor", "shortname": "Ex", "description": "Szabolcsi Tekergő"},
    {"arrival_time": "14:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "14:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "14:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "15:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "16:09", "headsign": "Balatonfüred", "shortname": "S", "description": "Tekergő"},
    {"arrival_time": "16:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "16:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "16:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "17:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "18:13", "headsign": "Tapolca", "shortname": "Ex", "description": "Csabai Tekergő"},
    {"arrival_time": "18:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "18:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "18:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "19:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "20:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "20:57", "headsign": "Balatonfüred", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "20:59", "headsign": "Budapest-Déli", "shortname": "S", "description": "VIZIPÓK Sebesvonat"},
    {"arrival_time": "21:35", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "22:15", "headsign": "Budapest-Déli", "shortname": "IR", "description": "KATICA InterRégió"},
    {"arrival_time": "22:34", "headsign": "Balatonfüred", "shortname": "S", "description": "Sebesvonat"},
    {"arrival_time": "22:34", "headsign": "Balatonfüred", "shortname": "S", "description": "Vonat"},
    {"arrival_time": "23:46", "headsign": "Székesfehérvár", "shortname": "S", "description": "BAGOLYVONAT"},
    {"arrival_time": "23:59", "headsign": "Balatonfüred", "shortname": "IR", "description": "KATICA InterRégió"}
]

output = []

for idx, train in enumerate(raw_trains):
    route_id = f"{train['description'].upper().replace(' ', '_')}_{train['arrival_time'].replace(':', '')}_{train['headsign'].upper().replace('-', '').replace(' ', '_')}"
    # Vonattípus színek hozzárendelése
    description_upper = train["description"].upper()
    if "INTERREGIO" in description_upper or "INTERRÉGIÓ" in description_upper:
        color = "008000"  # zöld
    elif "INTERCITY" in description_upper:
        color = "274F96"  # kék
    elif "SEBESVONAT" in description_upper:
        color = "274F96"  # kék
    elif "BAGOLYVONAT" in description_upper:
        color = "000000"  # lila
    elif "TEKERGŐ" in description_upper:
        color = "ED2F2F"  # aranysárga
    elif "VIZIPÓK" in description_upper:
        color = "3B3B3B"  # türkiz
    else:
        color = "000000"  # alapértelmezett fekete

    item = {
        "routeId": route_id,
        "headsign": train["headsign"],
        "stopTimes": [
            {
                "stopId": "STOP_FUZFO_ALLOMAS",
                "arrivalTime": train["arrival_time"],
                "departureTime": None,
                "tripId": f"OFFLINE_TRIP_{idx:02}",
                "stopSequence": 1
            }
        ],
        "shortName": train["shortname"],
        "description": train["description"],
        "type": "TRAIN",
        "color": color,
        "textColor": "FFFFFF",
        "vehicleName": "Vonat",
        "vehicletype": "RAIL",
        "tripDetails": [
            {
                "stop_id": "STOP_FUZFO_ALLOMAS",
                "stop_name": "Balatonfűzfő, vasútállomás",
                "stop_lat": 47.046356,
                "stop_lon": 18.057539,
                "arrival_time": train["arrival_time"],
                "departure_time": None,
                "stopSequence": 1
            }
        ]
    }
    output.append(item)

# Kiírás JSON fájlba
with open("menetrend_balatonfuzfo.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Fájl elkészült: menetrend_balatonfuzfo.json")
