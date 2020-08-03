from nmigen                                   import Elaboratable, Module, Signal

from contextlib import contextmanager

from luna.gateware.stream                     import StreamInterface
from luna.usb2                                import USBDevice, USBSignalInEndpoint
from luna.gateware.usb.usb2.request           import USBRequestHandler, StallOnlyRequestHandler
from luna.gateware.usb.usb2.endpoints.stream  import USBStreamInEndpoint, USBStreamOutEndpoint

from usb_protocol.types                       import USBRequestType,USBTransferType
from usb_protocol.emitters                    import DeviceDescriptorCollection
from usb_protocol.emitters.construct          import emitter_for_format
from usb_protocol.emitters.descriptors.hid    import HIDDescriptor,HIDReportDescriptorEmitter




class HIDDevice(Elaboratable):

    _STATUS_ENDPOINT_NUMBER = 1
    _DATA_ENDPOINT_NUMBER   = 4

    def __init__(self, *, bus, idVendor, idProduct,
        manufacturer_string="OrangeCrab",
        product_string="HID Register Reader",
        serial_number=None, max_packet_size=64):

        self._bus                 = bus
        self._idVendor            = idVendor
        self._idProduct           = idProduct
        self._manufacturer_string = manufacturer_string
        self._product_string      = product_string
        self._serial_number       = serial_number
        self._max_packet_size     = max_packet_size

        #
        # I/O port
        #
        self.connect = Signal()
        self.status  = Signal(10)

    def create_descriptors(self):
        descriptors = DeviceDescriptorCollection()

        hid_report = bytes([
            0x05, 0x01,         # USAGE_PAGE (Generic Desktop)
            0x09, 0x00,         # USAGE(Undefined)
            0xa1, 0x01,         # COLLECTION(Application)
            0x15, 0x00,         # LOGICAL_MINIMUM(0)
            0x26, 0x00, 0x04,   # LOGICAL_MAXIMUM(10 bit max)
            0x85, 0x01,         # REPORT_ID(1)
            0x75, 0x0a,         # REPORT_SIZE(10)
            0x95, 0x01,         # REPORT_COUNT(1)
            0x09, 0x00,         # USAGE(Undefined)
            0x81, 0x82,         # INPUT(Data, Var, Abs, Vol) - to the host
            0xc0                # END_COLLECTION
        ])

        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = self._idVendor
            d.idProduct          = self._idProduct

            d.iManufacturer      = self._manufacturer_string
            d.iProduct           = self._product_string
            d.iSerialNumber      = self._serial_number

            d.bNumConfigurations = 1
        with descriptors.ConfigurationDescriptor() as c:
            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0

                i.bInterfaceClass    = 0x03 # HID
                i.bInterfaceSubclass = 0x00 # No SubClass
                i.bInterfaceProtocol = 0x00 # No Protocol
                
                i.iInterface = 0x00

                hid_header = HIDDescriptor()
                hid_header.wDescriptorLength = len(hid_report)

                i.add_subordinate_descriptor(hid_header)

                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x80 | self._STATUS_ENDPOINT_NUMBER
                    e.bmAttributes     = USBTransferType.INTERRUPT
                    e.wMaxPacketSize   = self._max_packet_size
                    e.bInterval        = 1


        descriptors.add_descriptor(hid_report, 0x22)
        return descriptors

    def elaborate(self, platform):
        m = Module()

        # Create our core USB device, and add a standard control endpoint.
        m.submodules.usb = usb = USBDevice(bus=self._bus)
        control_ep = usb.add_standard_control_endpoint(self.create_descriptors())

        # Create an interrupt endpoint which will carry the value of our counter to the host
        # each time our interrupt EP is polled.
        status_ep = USBSignalInEndpoint(width=24, endpoint_number=1, endianness="little")
        usb.add_endpoint(status_ep)
        m.d.comb += [
            status_ep.signal[0:8].eq(0x01),
            status_ep.signal[8:].eq(self.status)
        ]

        # Connect our USB device
        m.d.comb += [
            usb.connect                .eq(self.connect)
        ]

        return m
