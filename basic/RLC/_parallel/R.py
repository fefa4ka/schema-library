from .. import Base
from bem.basic import Resistor
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    def willMount(self, R_parallel=1 @ u_Ohm):
        pass

    def circuit(self):
        super().circuit()

        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')

        R_parallel = self.input & Resistor()(self.R_parallel) & self.output
