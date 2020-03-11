from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    def willMount(self, C_gnd = 1 u_F):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('GndCapacitorOutput')

        C_gnd = signal & self.output & Capacitor()(value=self.C_gnd, **self.load_args) & self.gnd
