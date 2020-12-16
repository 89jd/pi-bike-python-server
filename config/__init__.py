import json
from types import SimpleNamespace

with open('server.json') as f:
    properties = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
