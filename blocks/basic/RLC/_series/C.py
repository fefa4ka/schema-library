from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_series = 1 @ u_F

    def willMount(self, C_series):
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

        C_out = Capacitor()(value=self.C_series, ref='C_s', **self.load_args)

        circuit = signal & C_out['+', '-'] & self.output 