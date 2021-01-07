import socketio
import json
from flask import Flask, send_from_directory
from typing import Callable
from config import properties

class BikeDataServer():
    def __init__(self,) -> None:
        sio = socketio.Server(async_mode='threading', cors_allowed_origins="*")

        self.app = Flask(__name__)
        self.app.wsgi_app = socketio.WSGIApp(sio, self.app.wsgi_app)

        debug_image = getattr(properties, "debug_image_file", None)
        
        if debug_image:
            @self.app.route('/static/lcd-image.png')
            def send_lcd():
                return send_from_directory("/".join(debug_image.split('/')[0:-1]), debug_image.split('/')[-1])
        
        self.on_exercise_started: Callable[[str], None] = None
        self.on_exercise_stopped: Callable[[str], None] = None
        self.on_reset_exercise: Callable[[str], None] = None
        self.on_heart_rate_received: Callable[[str], None] = None
        self.on_paused: Callable[[str], None] = None
        self.on_resumed: Callable[[str], None] = None
        self.on_connected: Callable[[str], None] = None
        self.on_gear_decreased: Callable[[str], None] = None
        self.on_gear_increased: Callable[[str], None] = None
        self.on_toggle_pause: Callable[[], None] = None
        
        self.sio = sio 

        @sio.event
        def connect(sid, environ):
            self.on_connected(sid)

        @sio.event
        def disconnect(sid):
            print('disconnect ', sid)

        @sio.event
        def start_exercise(sid, data=None):
            self.on_exercise_started(sid)

        @sio.event
        def reset_exercise(sid, data=None):
            self.on_reset_exercise(sid)

        @sio.event
        def pause_exercise(sid, data=None):
            self.on_paused(sid)

        @sio.event
        def resume_exercise(sid, data=None):
            self.on_resumed(sid)

        @sio.event
        def toggle_pause(sid, data=None):
            self.on_toggle_pause(sid)

        @sio.event
        def finish_exercise(sid, data=None):
            self.on_exercise_stopped(sid)

        @sio.event
        def decrease_gear(sid, data=None):
            self.on_gear_decreased(sid)

        @sio.event
        def heart_rate(sid, data):
            self.on_heart_rate_received(data)

        @sio.event
        def increase_gear(sid, data=None):
            print('increase_gear')
            self.on_gear_increased(sid)

    def emit_exercise_data(self, data):
        self.sio.emit('exercise_data', data)
    
    def emit_idle_state(self, state):
        self.sio.emit('idle_state', state)

    def emit_gear(self, gear):
        self.sio.emit('gear', gear)
    
    def emit_duration(self, duration):
        self.sio.emit('duration', duration)

    def start(self):
        self.app.run(use_reloader=False, debug=False, threaded=True, host=properties.host)

if __name__ == '__main__':
    BikeDataServer().start()