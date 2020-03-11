from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    def willMount(self, C_series=1 @ u_F):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('SeriesCapacitorOutput')

        C_series = signal & Capacitor()(self.C_series) & self.output
