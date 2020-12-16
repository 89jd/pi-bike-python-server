from server import BikeDataServer
from bikesensor import BikeSensor
from routine import BikeRoutine
import threading
import logging
import sys
from utils import print_debug

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

routine = None
gear = 8

def initialise_routine():
    print_debug('Initialise routine')
    global gear
    global routine

    if routine: 
        print_debug("stopping existing")
        routine.stop()

    routine = BikeRoutine(gear, lambda: BikeSensor())

    routine.on_update = server.emit_exercise_data
    routine.on_idle_cb = server.emit_idle_state
    routine.on_duration_update = server.emit_duration
    
    #server.on_exercise_started = lambda _: not routine.stop() and routine.start()
    server.on_reset_exercise = lambda _: initialise_routine()
    server.on_paused = lambda _: routine.force_pause()
    server.on_resumed = lambda _: routine.resume()
    
    def increase_gear():
        global gear
        gear += 1
        server.emit_gear(gear)
        routine.gear = gear
    
    def decrease_gear():
        global gear
        gear -= 1
        server.emit_gear(gear)
        routine.gear = gear

    server.on_gear_increased = lambda _: increase_gear()
    server.on_gear_decreased = lambda _: decrease_gear()
    server.on_heart_rate_received = lambda heart_rate: routine.publish_heartrate(heart_rate)
    
    def toggle_pause():
        if routine.paused:
            routine.resume()
        else:
            routine.force_pause()
        
    server.on_toggle_pause = lambda _: toggle_pause()

    server.emit_gear(gear)

    threading.Thread(target=routine.start, daemon=True).start()
        
print_debug('Start server')

server = BikeDataServer()
server.on_exercise_stopped = lambda _: initialise_routine()
initialise_routine()

server.on_connected = lambda _: print_debug('Client connected')

if __name__ == '__main__':
    server.start()
