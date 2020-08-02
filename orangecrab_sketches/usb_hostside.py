import evdev
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
orangecrab = [dev for dev in devices if "OrangeCrab" in dev.name][0]
for event in orangecrab.read_loop():
    if event.code:
        print(event)