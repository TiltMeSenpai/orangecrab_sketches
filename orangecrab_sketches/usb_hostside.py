import evdev, asyncio
from collections import deque
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter

async def read_adc():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    orangecrab = [dev for dev in devices if "OrangeCrab" in dev.name][0]
    async for event in orangecrab.async_read_loop():
       if event.code:
           val_pct = event.value / 255
           print("#" * int(val_pct * 100))
asyncio.run(read_adc())