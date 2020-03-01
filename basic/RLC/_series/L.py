from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_series = 1 @ u_H

    def willMount(self, L_series):
        pass

    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('SeriesInductorOutput')

        L_out = Inductor()(value=self.L_series, ref='L_s', **self.load_args)

        circuit = signal & L_out & self.output 
