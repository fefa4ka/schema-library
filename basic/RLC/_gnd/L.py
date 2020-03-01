from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_gnd = 1 @ u_H

    def willMount(self, L_gnd):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('GndInductorOutput')


        L_out = Inductor()(value=self.L_gnd, ref='L_g', **self.load_args)

        circuit = signal & self.output & L_out & self.gnd
