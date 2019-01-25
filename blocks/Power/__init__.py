
from bem import Block
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V


class Base(Block):
    source = None
    gnd = None
    def __init__(self, source=None, gnd=None):
        self.element = source

        self.circuit(gnd)

    @subcircuit
    def circuit(self, gnd=None):
        if gnd:
            self.gnd = gnd
        else:
            self.gnd = Net()

        if self.element:
            VCC = self.element['VCC'] if hasattr(self.element, 'VCC') else self.element[1]
            GND = self.element['GND'] if hasattr(self.element, 'GND') else self.element[2]
            self.input = self.v_ref = VCC
            self.gnd += GND
        else:
            self.input = self.v_ref = Net('VCC')

        self.input_n = self.output_n = self.gnd

        return 'Power'