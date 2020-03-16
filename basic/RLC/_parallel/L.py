from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    def willMount(self, L_parallel = 1 @ u_H):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('RLCOutput')

        L_parallel = signal & Inductor()(self.L_parallel) & self.output
