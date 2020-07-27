from nmigen import *
class Popcount(Elaboratable):
    def __init__(self, sig_in):
        self.bit_width = sig_in.shape().width
        self.sig_in = sig_in
        self.acc = []
        self.output = Signal(range(self.bit_width + 1))
        for i in range(int(self.bit_width / 4)):
            self.acc.append(Signal(3, name=f"acc_{i}"))
        
    def elaborate(self, platform):
        m = Module()
        for sig, i in zip(self.acc, range(0, self.bit_width, 4)):
            with m.Switch(self.sig_in[i:i+4]):
                for n in range(16):
                    with m.Case(n):
                        m.d.sync += sig.eq(bin(n).count("1"))
        m.d.sync += self.output.eq(sum(self.acc))
        return m

class CrabADC(Elaboratable):
    def __init__(self, bit_width = 8):
        self.sample_queue = Signal(2 ** bit_width)
        # self.popcount = Popcount(self.sample_queue)
        self.adc_mux  = Signal(4, reset=0x01)
        self.enable   = Signal()
        self.valid    = Signal()
        self.output   = Signal(bit_width)

    def elaborate(self, platform):
        m = Module()

        # m.submodules.popcount = self.popcount
        out_count = Signal()

        adc = platform.request("adc")
        flush_timer = Signal(range(self.sample_queue.shape().width), reset=self.sample_queue.shape().width - 1)
        with m.If(flush_timer == 0):
            m.d.sync += self.valid.eq(1)
        with m.Else():
            m.d.sync += [
                self.valid.eq(0),
                flush_timer.eq(flush_timer - 1)
            ]
        with m.If(self.adc_mux != adc.mux):
            m.d.sync += [
                adc.mux.eq(self.adc_mux),
                flush_timer.eq(flush_timer.reset)
            ]
        m.d.sync += [
            adc.ctrl[0].eq(adc.sense),
            adc.ctrl[1].eq(self.enable),
            Cat(out_count, self.sample_queue).eq(Cat(self.sample_queue, adc.sense))
        ]
        with m.If(out_count == 1):
            m.d.sync += self.output.eq(self.output + 1)
        with m.Else():
            with m.If(self.output != 0):
                m.d.sync += self.output.eq(self.output - 1)
        return m