import math

from nmigen import *

class SinTable(Elaboratable):
    def __init__(self, inport: Signal, outport: Signal):
        self.should_invert  = inport[-1]
        self.should_reverse = inport[-2]
        self.inport         = inport[:-2]
        self.outport = outport
        self.table_width = (2 ** (inport.width - 2))
        steps = [n / self.table_width for n in range(0, self.table_width)]
        print(steps)
        sin_table = [ int( math.sin(0.5 * math.pi * n) * (2 ** (outport.width - 1))) for n in steps]
        self.table = Memory(width = outport.width, depth = self.table_width, init = sin_table)

    def elaborate(self, platform):
        m = Module()
        m.submodules.rdport = r = self.table.read_port()
        with m.If(self.should_reverse == 0):
            m.d.sync += r.addr.eq(self.inport)
        with m.Else():
            m.d.sync += r.addr.eq(self.table_width - self.inport - 1)
        with m.If(self.should_invert == 0):
            m.d.sync += self.outport.eq(r.data)
        with m.Else():
            m.d.sync += self.outport.eq((-1 * r.data))
        return m