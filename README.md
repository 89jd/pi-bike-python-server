# pi-bike-server

## Installation
```
git clone https://github.com/89jd/pi-bike-server
cd pi-bike-server
git submodule init
git submodule update
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py [debug]
```

## Config File example

```json
{
    "revolution_sensor": {
        "pin": 21,
        "idle_time": 4000
    },
    "firebase": { 
        "config_file": "firebase.json",
        "collection": "workouts",
        "list_values_key": "revolutions" 
    },
    "bike": {
        "revolution_distance": 4
    },
    "debug_image_file": "/some/location/lcd-image.png",
    "host": "0.0.0.0" 
}
```
| Field      | 
| ----------- |
| revolution_sensor      |
| firebase   | Optional
| bike   | 
|debug_image_file | string - optional|
|host | string |



| Field      | Description |
| ----------- | ----------- |
| pin      | int. The GPIO pin on the pi which the bike is plugged into (reed switch)  |
| idle_time   | How long until the counting / tracking will stop if idle        |

| Field      | Description |
| ----------- | ----------- |
| config_file      | String. File location that contains firebase details  |
| collection   | Table to store workouts in   |
| list_values_key   | object within the document to store each revolution and its corresponding data  |

| Field      | Description |
| ----------- | ----------- |
| revolution_distance      | int. Corresponds to the distance one revolution equates to. Got this value from the existing bike computer
