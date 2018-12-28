
from bem import Block
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V


class Base(Block):
    @subcircuit
    def create_circuit(self, source=None, gnd=None):
        instance = self.clone
        if gnd:
            instance.gnd = gnd
        else:
            if self.DEBUG:
                from skidl.pyspice import gnd
                instance.gnd = gnd
            else:
                instance.gnd = Net('Groud')

        if source:
            instance.element = source
            VCC = instance.element['VCC'] if hasattr(source, 'VCC') else instance.element[1]
            GND = instance.element['GND'] if hasattr(source, 'GND') else instance.element[2]
            
            instance.input = instance.output = VCC
            instance.gnd += GND
        else:
            instance.input = instance.output = Net('VCC')

        return instance