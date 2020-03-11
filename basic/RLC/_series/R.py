from .. import Base
from bem.basic import Resistor 
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    def willMount(self, R_series=1 @ u_Ohm):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('SeriesResistorOutput')

        R_series = signal & Resistor()(value=self.R_series, **self.load_args) & self.output
