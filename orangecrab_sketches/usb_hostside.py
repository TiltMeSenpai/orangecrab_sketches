import evdev, asyncio, os, functools, json
from collections import deque
from quart import *

class AdcDashboard:
    data_queue = deque(maxlen=1000)

    @functools.cached_property
    def dashboard_file(self):
        with open(os.path.join(os.path.dirname(__file__), "../index.html")) as f:
            return f.read()

    async def read_adc(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        orangecrab = [dev for dev in devices if "OrangeCrab" in dev.name][0]
        async for event in orangecrab.async_read_loop():
            if event.code:
                yield (event.timestamp(), event.value)

    async def run(self):
        async for event in self.read_adc():
            print(event.timestamp(), event.value)

adc = AdcDashboard()
app = Quart(__name__)

@app.route("/")
async def main():
    return adc.dashboard_file

@app.websocket("/ws")
async def ws():
    async for event in adc.read_adc():
        await websocket.send(json.dumps(event))

app.run()