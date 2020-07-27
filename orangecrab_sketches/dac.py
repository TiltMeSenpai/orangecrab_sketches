from nmigen import *

class PWM(Elaboratable):
    def __init__(self, inport: Signal, out: Signal):
        self.inport = inport
        self.out = out
        self.inport_stash = Signal(inport.width)
        self.accumulator  = Signal(inport.width, reset = ((2 ** inport.width) - 1))
    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.out.eq(self.inport_stash > self.accumulator)
        m.d.sync += self.accumulator.eq(self.accumulator - 1)
        with m.If(self.accumulator == 0):
            m.d.sync += [
                self.accumulator.eq(self.accumulator.reset),
                self.inport_stash.eq(self.inport)
            ]
        return m

class DeltaSigma(Elaboratable):
    def __init__(self, in_port: Signal, out_port: Signal):
        self.in_port  = in_port
        self.out_port = out_port
        self.accumulator = Signal(in_port.width + 1)
    
    def elaborate(self, platform):
        m = Module()

        m.d.sync += self.out_port.eq(self.accumulator[-1])
        m.d.sync += self.accumulator.eq(self.accumulator[:-1] + self.in_port)

        return m