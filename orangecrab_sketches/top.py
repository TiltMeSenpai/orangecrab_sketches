from nmigen import *
from nmigen.build import Resource, Pins, Attrs

from luna.gateware.usb.devices.acm import USBSerialDevice

from .clock import OrangeCrabDomainGenerator
from .capsense import Capsense
from .adc import CrabADC
from .dac import *

class USBSerialDeviceExample(Elaboratable):
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
                USBSerialDevice(bus=bus, idVendor=0x16d0, idProduct=0x0f3b)
        
        m.d.comb += [
            # Place the streams into a loopback configuration...
            usb_serial.tx.payload  .eq(usb_serial.rx.payload),
            usb_serial.tx.valid    .eq(usb_serial.rx.valid),
            usb_serial.tx.first    .eq(usb_serial.rx.first),
            usb_serial.tx.last     .eq(usb_serial.rx.last),
            usb_serial.rx.ready    .eq(usb_serial.tx.ready),
            
            # ... and always connect by default.
            usb_serial.connect     .eq(1)
        ]

        return m

class Main(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        # capsense = platform.request("capsense", 0)
        usrbtn   = platform.request("button", 0)
        programn = platform.request("program", 0)

        m.submodules.adc = adc = CrabADC()
        m.submodules.dac = PWM(adc.output, platform.request("rgb_led", 0).g)

        # m.submodules.serial = USBSerialDeviceExample(adc)


        m.d.sync += [
            programn.eq(usrbtn)
        ]

        return m