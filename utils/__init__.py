from time import time
import sys

debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

current_millis = lambda: int(round(time() * 1000))

x = 0

def increase_test_millis_by(i):
    global x
    x += i

debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

def print_debug(s):
    if debug:
        print(s)