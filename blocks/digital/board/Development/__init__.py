from bem.abstract import Electrical, Network
from bem.analog.voltage import Regulator
from bem.digital import Microcontroller
from skidl import Part
from bem import u_V
import re
from collections import defaultdict

class Base(Electrical()):
    def circuit(self):
        power_5V = Regulator(via='ic')(V = 10 @ u_V, V_out = 5 @ u_V)
        power_5V.input += self.v_ref
        power_5V.gnd += self.gnd
        
        mcu = Microcontroller(
            vendor='Microchip_ATmega',
            series='ATmega8',
            reset='switch')(frequency = 8000000)
            
        mcu_supply = power_5V & mcu

        # Interface conntectors
        interfaces = {}
        for interface in mcu.mods['interface']:
            connector_builder = getattr(mcu, interface + '_connector')
            interfaces[interface] = connector_builder()

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

        
        