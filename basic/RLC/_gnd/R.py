from .. import Base
from bem.basic import Resistor
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_gnd = 1 @ u_Ohm

    def willMount(self, R_gnd):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('GndResistorOutput')

        R_gnd = signal & self.output & Resistor()(value=self.R_gnd, **self.load_args) & self.gnd
