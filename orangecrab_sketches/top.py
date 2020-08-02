from nmigen import *
from nmigen.build import Resource, Pins, Attrs

from luna.gateware.usb.devices.acm import USBSerialDevice

from .clock import OrangeCrabDomainGenerator
from .capsense import Capsense
from .adc import CrabADC
from .dac import PWM
from .hid import HIDDevice
from .tables import SinTable

class USBDevice(Elaboratable):
    """ Device that acts as a 'USB-to-serial' loopback using our premade gateware. """
    def __init__(self, adc):
        self.adc = adc

    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = OrangeCrabDomainGenerator()

        # Create our USB-to-serial converter.
        bus = platform.request("usb")
        m.submodules.usb_serial = usb_serial = \
                HIDDevice(bus=bus, idVendor=0x1337, idProduct=0x1337)
        
        m.d.comb += [
            # Place the streams into a loopback configuration...
            usb_serial.status.eq(self.adc),
            # ... and always connect by default.
            usb_serial.connect.eq(1)
        ]

        return m

class Main(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        usrbtn   = platform.request("button", 0)
        programn = platform.request("program", 0)
        rgb_led = platform.request("rgb_led", 0)

        m.submodules.adc = adc = CrabADC()
        m.submodules.dac = PWM(adc.output, rgb_led.g)

        m.submodules.hid = USBDevice(adc.output)


        m.d.sync += [
            programn.eq(usrbtn)
        ]

        return m