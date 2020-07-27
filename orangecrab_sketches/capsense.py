from nmigen import *

class Capsense(Elaboratable):
    def __init__(self, pin):
        self.pin = pin

    def elaborate(self, platform):
        m = Module()
        freq = platform.default_clk_frequency
        timer = Signal(range(int(freq // 1000)), reset=int((freq // 1000) - 1))
        pin = self.pin

        m.d.comb += pin.o.eq(0)
        with m.FSM():
            with m.State("CHARGE"):
                m.d.comb += pin.oe.eq(1)
                m.d.sync += timer.eq(timer - 1)
                with m.If(timer == 0):
                    m.next = "DISCHARGE"
            with m.State("DISCHARGE"):
                m.d.sync += timer.eq(timer.reset)
                with m.If(pin.i == 1):
                    m.next = "CHARGE"
        return m