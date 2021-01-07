from bem.abstract import Electrical, Network, Physical
from bem.basic import Diode, Plug
from bem.analog.voltage import Regulator
from bem.analog.driver import Led
from bem.digital import Microcontroller
from bem.digital.adapter import UsbUart
from bem import u_V, u_Hz
import re
from collections import defaultdict

class Base(Electrical()):
    """

    ```
    vs = VS(flow='V')(V=5)
    mcu = Example()
    vs & mcu.v_ref
    mcu.gnd & vs

    watch = mcu
    ```
    """
    def willMount(self, V_mcu=5 @ u_V, series='ATmega8', frequency=8e6 @ u_Hz):
        pass

    def circuit(self):
        mcu = Microcontroller(
            series=self.series,
            reset='switch')(V=self.V_mcu, frequency=self.frequency)

        self.V_max = mcu.V * 2

        power = Regulator(via='ic')(V=self.V_max, V_out=mcu.V)
        self.v_ref & power
        self.gnd & power.gnd

        power & mcu

        supply_indication = power & Led(via='resistor')(V=power.V_out, diodes=Diode(type='led')(V=power.V_out, color='green'))

        usb = mcu & UsbUart(via='atmega16u2')(V=power.V_out) & Plug(interface='usb', type='b')()

        interfaces = {}
        for interface in mcu.mods['interface']:
            interfaces[interface] = mcu & Plug(interface=interface)(ref=interface)

        buses = defaultdict(list)
        for pin in mcu.element.pins:
            port = re.match(r'([A-Z]{1,3})([0-9]{1,3})', pin.name)
            if port:
                port, bit = port.groups()
                buses[port].append(port + bit)

        return True

        for bus in buses.keys():
            bus_width = len(buses[bus])
            if bus_width > 1:
                connector = Physical(part='Connector_Generic:Conn_01x0' + str(bus_width), footprint='Connector_PinHeader_2.54mm:PinHeader_1x0' + str(bus_width) + '_P2.54mm_Vertical')(ref=bus)
                for index, pin in enumerate(buses[bus]):
                    connector[index + 1] & mcu[pin]




