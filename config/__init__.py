import json
from types import SimpleNamespace

with open('server.json') as f:
    properties = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

if not hasattr(properties.revolution_sensor, 'debug_sensor'):
    properties.revolution_sensor.debug_sensor = False