from .. import Base
from bem.basic import Resistor
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    def willMount(self, R_gnd=1 @ u_Ohm):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('GndResistorOutput')

        R_gnd = signal & self.output & Resistor()(self.R_gnd) & self.gnd
