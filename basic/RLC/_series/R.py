from .. import Base
from bem.basic import Resistor
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    def willMount(self, R_series=1000 @ u_Ohm):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('SeriesResistorOutput')

        R_series = signal & Resistor()(self.R_series) & self.output
