from nmigen.build import Pins, Resource, Attrs
from nmigen_boards.orangecrab_r0_2 import OrangeCrabR0_2Platform

from .top import Main


if __name__ == "__main__":
    import os
    os.environ["NEXTPNR_ECP5"] = "yowasp-nextpnr-ecp5"
    os.environ["ECPPACK"] = "yowasp-ecppack"
    platform = OrangeCrabR0_2Platform()
    platform.add_resources([
        Resource("sync_out", 0, Pins("1", conn=("io", 0), dir="o"), Attrs(IO_TYPE="LVCMOS33"))
    ])
    platform.build(Main(), do_program=True)