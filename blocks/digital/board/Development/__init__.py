from bem.abstract import Electrical, Network
from bem.basic import Diode, Plug
from bem.analog.voltage import Regulator
from bem.analog.driver import Led
from bem.digital import Microcontroller
from skidl import Part
from bem import u_V, u_Hz
import re
from collections import defaultdict

class Base(Electrical()):
    series = 'ATmega8'
    frequency = 8000000 @ u_Hz

    def willMount(self, series, frequency):
        pass

    def circuit(self):
        mcu = Microcontroller(
            series=self.series,
            reset='switch')(frequency=self.frequency)

        self.V_max = mcu.V * 2 

        power = Regulator(via='ic')(V=self.V_max, V_out=mcu.V)
        mcu_supply = Plug(power='dc')(V=self.V_max) & power & mcu
        supply_indication = power & Led(via='resistor')(diodes=Diode(type='led')(color='green'))

        interfaces = {}
        for interface in mcu.mods['interface']:
            interfaces[interface] = mcu & Plug(interface=interface)(ref=interface)

        buses = defaultdict(list)
        for pin in mcu.element.pins:
            port = re.match(r'([A-Z]{1,3})([0-9]{1,3})', pin.name)
            if port:
                port, bit = port.groups()
                buses[port].append(port + bit)

        for bus in buses.keys():
            bus_width = len(buses[bus])
            if bus_width > 1:
                connector = Part('Connector_Generic', 'Conn_01x0' + str(bus_width), footprint='Connector_PinHeader_2.54mm:PinHeader_1x0' + str(bus_width) + '_P2.54mm_Vertical', ref=bus)
                for index, pin in enumerate(buses[bus]):
                    connector[index + 1] += mcu[pin]



