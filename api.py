from fastapi import FastAPI, status
from fastapi.responses import FileResponse, PlainTextResponse

from pydantic import BaseModel

import subprocess

#
# Define functions to talk to the hardware
#
# Here we use toy examples from /sys appropriate to
# a Raspberry Pi.
#
# They might need root access, so run stuff in a shell
# inside sudo.
#
def run_as_root(cmd):
    x = subprocess.run(["sudo", "su", "-c", cmd]
                       , capture_output=True
                       , text=True
                       , check=True)
    return x.stdout.strip()

def temp_read():
    raw = run_as_root("cat /sys/class/thermal/thermal_zone0/temp")
    t = f"{int(raw) / 1000.0:.1f}\N{DEGREE SIGN}C"
    return { 'temperature': t }

def led_init():
    run_as_root("echo none > /sys/class/leds/led0/trigger")

def led_set(x):
    b = 255 if x > 0 else 0
    run_as_root(f"echo {b} > /sys/class/leds/led0/brightness")

def led_get():
    b = float(run_as_root("cat /sys/class/leds/led0/brightness"))
    x = 1.0 if b > 0 else 0.0
    return { 'brightness': x }

#
# The main HTTP server starts here
#

led_init()

app = FastAPI()

apiroot = "/api"

def client_error(t):
    return PlainTextResponse(content = t
                , status_code = status.HTTP_400_BAD_REQUEST)

@app.get('/')
def get_index():
    return FileResponse('index.html')

@app.get(apiroot)
def get_all():
    return (temp_read() | led_get())

@app.get(apiroot + "/temperature")
def get_temp():
    return temp_read()

@app.get(apiroot + "/light")
def get_light():
    return led_get()

class LightControl(BaseModel):
    brightness: float

@app.put(apiroot + "/light")
def put_light(m: LightControl):
    b = m.brightness
    if b < 0.0 or b > 1.0:
        return client_error(f"Brightness {b} out of range [0,1]")
    else:
        led_set(b)
        return led_get()
