from fastapi import FastAPI
from fastapi.responses import FileResponse

from pydantic import BaseModel

def temp_read():
    return { 'temperature': '123.45C' }

def led_init():
    print("Initialized LEDs")

def led_set(x):
    print(f"LED brightness({x})")

def led_get():
    return { 'brightness': 0.5 }


led_init()

app = FastAPI()

apiroot = "/api"

@app.get('/')
def get_index():
    return FileResponse('index.html')

@app.get(apiroot)
def get_all():
    return (temp_read() | led_get() )

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
    x = m.brightness
    led_set(x)
    return led_get()
