import cv2 as cv
import numpy as np
from datetime import datetime
from subprocess import Popen, PIPE
now = datetime.now

DEVICE = '/dev/input/event3'
EV_ABS = 0x0003
EV_KEY = 0x0001
EV_SYN = 0x0000
SYN_REPORT = 0x0000
BTN_TOOL_FINGER = 0x0145
ABS_MT_SLOT = 0x002f
ABS_MT_TOUCH_MAJOR = 0x0030
ABS_MT_TOUCH_MINOR = 0x0031
ABS_MT_POSITION_X = 0x0035
ABS_MT_POSITION_Y = 0x0036
ABS_MT_TRACKING_ID = 0x0039
DOWN = 0x00000001
UP = 0x00000000
event_pattern = "sendevent {} {:d} {:d} {:d}"

def key_event(key):
    assert(isinstance(key, int))
    proc = Popen(args = "adb shell input keyevent {}".format(key), shell = True)
    return proc

def back():
    return key_event(4)

def home():
    return key_event(3)


def tap(x,y):
    assert(isinstance(x, int) and isinstance(y, int))
    proc = Popen(args = "adb shell input tap {} {}".format(x,y), shell = True)
    return proc
    
def swipe(x0,y0,x1,y1,dur = 100):
    for var in [x0, y0, x1, y1, dur]:
        assert(isinstance(var, int))
    proc = Popen(args = "adb shell input swipe {} {} {} {} {}".format(x0,y0,x1,y1,dur), shell = True)
    return proc
    
def long_tap(x,y,dur = 1000):
    return swipe(x,y,x,y,dur)
    
def scroll_down(x, y, dur = 3000, dist = 500):
    return swipe(x,y,x,y-dist,dur)
    
def scroll_up(x, y, dur = 3000, dist = 500):
    return swipe(x,y,x,y+dist,dur)

def scroll_left(x, y, dur = 3000, dist = 500):
    return swipe(x,y,x+dist,y,dur)

def scroll_right(x, y, dur = 3000, dist = 500):
    return swipe(x,y,x-dist,y,dur)
    
def devices():
    proc = Popen(args = ["adb", "devices"], stdout = PIPE)
    print proc.communicate()[0]
    
def connect(ip):
    ip = str(ip)
    proc = Popen(args = ["adb", "connect", ip + ":5555"], stdout = PIPE)
    print proc.communicate()[0]
    
def disconnect(ip):
    ip = str(ip)
    proc = Popen(args = ["adb", "disconnect", ip + ":5555"], stdout = PIPE)
    print proc.communicate()[0]
    
def disconnect_all():
    proc = Popen(args = ["adb", "disconnect"], stdout = PIPE)
    print proc.communicate()[0]
    
def raw_screenshot():
    proc = Popen(args = "adb shell screencap -p", shell = True, stdout = PIPE)
    raw = ""
    while proc.poll() is None:
        stdout, _= proc.communicate()
        raw += stdout
    raw = raw.replace("\r\n", "\n")
    return raw
    

def take_screenshot():
    raw = raw_screenshot()
    im = cv.imdecode(np.frombuffer(raw, np.uint8), cv.IMREAD_UNCHANGED)
    return im
    
def save_screenshot(filename = None):
    t = now().strftime("%Y%m%dT%H%M%S")
    filename = filename or ("screencap" + t + ".png")
    raw = raw_screenshot()
    with open(filename, "wb+") as outfile:
        outfile.write(raw)
    return True

def close_app(app_name):
    proc = Popen(args = "adb shell am force-stop {}".format(app_name), shell = True)
    return proc

def open_app(app_name):
    proc = Popen(args = "adb shell monkey -p {} 1".format(app_name), shell = True)
    return proc
    
def build_cmd(cmd):
    return 'adb shell "' + '; '.join(cmd) + '"'

def send_event(f):
    def send_f(*args):
        cmd = build_cmd(f(*args))
        p = Popen(cmd, shell = True, stdout = PIPE)
        return p.communicate()
    return send_f

@send_event
def finger_down(x, y, finger = 0, slot = 0):
    cmd = [
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_SLOT, slot),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_TRACKING_ID, finger),
        event_pattern.format(DEVICE, EV_KEY, BTN_TOOL_FINGER, DOWN),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_X, x),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_Y, y),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_TOUCH_MAJOR, 6),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_TOUCH_MINOR, 5),
        event_pattern.format(DEVICE, EV_SYN, SYN_REPORT, 0)
    ]
    finger += 1
    slot += 1
    return cmd

@send_event
def finger_up(slot):
    cmd = [
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_SLOT, slot),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_TRACKING_ID, -1),
        event_pattern.format(DEVICE, EV_KEY, BTN_TOOL_FINGER, UP),
        event_pattern.format(DEVICE, EV_SYN, SYN_REPORT, 0)
    ]
    return cmd

@send_event
def finger_update_y(slot, y):
    cmd = [
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_SLOT, slot),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_Y, y),
        event_pattern.format(DEVICE, EV_SYN, SYN_REPORT, 0)
    ]
    return cmd

@send_event
def finger_update_x(slot, x):
    cmd = [
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_SLOT, slot),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_X, x),
        event_pattern.format(DEVICE, EV_SYN, SYN_REPORT, 0)
    ]
    return cmd    

@send_event
def finger_update(slot, x, y):
    cmd = [
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_SLOT, slot),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_X, x),
        event_pattern.format(DEVICE, EV_ABS, ABS_MT_POSITION_Y, y),
        event_pattern.format(DEVICE, EV_SYN, SYN_REPORT, 0)
    ]
    return cmd 