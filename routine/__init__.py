from collections import deque
from datetime import datetime
from firebase import Firebase
from time import sleep, time
from bikesensor import BikeSensor
from statistics import mean
from typing import Callable
from utils import current_millis, print_debug
from threading import Thread
from config import properties

metres_per_seconds_history = deque(maxlen=5)

class BikeRoutine():
    def __init__(self, gear, sensor_factory: Callable[[], BikeSensor]) -> None:
        self.initialise()
        self.gear = gear
        self.timer_thread = None
        self.timer_thread_factory = lambda: TimerThread(self)
        self.on_update: Callable[[dict],None] = None
        self.on_idle_cb: Callable[[bool],None] = None
        self.on_duration_update: Callable[[int], None] = None
        self.sensor_factory = sensor_factory
        self.sensor = None
        self.heart_rate_updated = None
        self.data_points = []
        self.firebase = Firebase()

    def start_timer(self):
        self.stop_timer()

        self.timer_thread = self.timer_thread_factory()
        self.timer_thread.start()
    
    def stop_timer(self):
        if self.timer_thread:
            self.timer_thread.stop = True

    def initialise(self):
        self.paused = False
        self.start_time = -1
        self.revolutions = 0
        self.total_time = 0
        self.duration = 0
        self.heart_rate = 0

    def on_idle(self, is_idle):
        if is_idle:
            self._pause()
        else:
            self.resume()

        if self.on_idle_cb:
            self.on_idle_cb(is_idle)

    def on_revolution(self, t: float):
        if not self.paused:
            if t == -1 or self.start_time == -1:
                if self.start_time == -1:
                    self.start_timer()
                    self.start_time = current_millis()
            else:
                self.revolutions += 1
                if self.on_update:
                    self.on_update(self._calculate_values_from_rev(t))

    def _pause(self):
        self.paused = True
        self.stop_timer()

    def force_pause(self):
        self._pause()
        if self.sensor != None:
            self.sensor.pause()

    def resume(self):
        self.start_timer()
        self.paused = False
        if self.sensor != None:
            self.sensor.resume()

    def save_data_point(self, data_point):
        self.data_points.append(data_point)
        
    def _calculate_values_from_rev(self, time_in_seconds):  
        self.total_time += time_in_seconds
        distance_in_metres = 3.4 #Matches exercise bike speed 
        distance_in_metres = properties.bike.revolution_distance
        metres_per_seconds = distance_in_metres / time_in_seconds
        metres_per_seconds_history.append(metres_per_seconds)        
        average_metres_per_seconds = mean(metres_per_seconds_history)

        total_average_speed = (self.revolutions * distance_in_metres) / self.total_time
        
        x =  {
            "last_rev_time": time_in_seconds,
            "total_revs": self.revolutions,
            "distance": self.revolutions * distance_in_metres / 1000,
            "rpm": 60 / time_in_seconds,
            "current_speed": average_metres_per_seconds * 3.6,
            "total_average_speed": total_average_speed * 3.6,
            "gear": self.gear,
            "duration": self.duration,
            "time": current_millis() * 1000000
        }

        if self.heart_rate_updated and self.heart_rate > 0:
            x['heartrate'] = self.heart_rate
            self.heart_rate = 0
        
        self.data_points.append(x)
        
        return x

    def on_bike_ride_started(self):
        self.start_time = current_millis()

    def publish_heartrate(self, heartrate):
        self.heart_rate = heartrate
        self.heart_rate_updated = current_millis()

    def stop(self):
        data_points = self.data_points
        Thread(target=self.firebase.write_workout, args=(data_points,), daemon=True,).start()
        self.stop_timer()
        if self.sensor:
            self.sensor.stop()
    
    def start(self):
        self.initialise()
        if self.sensor:
            self.sensor.recording = False
        self.sensor = self.sensor_factory()
        self.sensor.on_revolution = self.on_revolution
        self.sensor.on_idle = self.on_idle
        self.sensor.start(debug=False)

def test():
    br = BikeRoutine(lambda: BikeSensor())
    br.on_update = print
    br.on_idle_cb = lambda b: print(f"Idle: {b}")
    br.start()

class TimerThread(Thread):
    def __init__(self, bike_routine: BikeRoutine) -> None:
        super().__init__(daemon=True)
        print_debug('New Timer Thread')

        self.bike_routine = bike_routine
        self.stop = False
        self.is_running = False
    
    def run(self) -> None:
        self.stop = False
        while not self.stop:
            self.is_running = True
            sleep(1)
            self.bike_routine.duration += 1
            if self.bike_routine.on_duration_update:
                self.bike_routine.on_duration_update(self.bike_routine.duration)

        self.is_running = False


if __name__ == "__main__":
    test()