from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    def willMount(self, L_parallel = 1 @ u_H):
        pass

    def circuit(self):
        super().circuit()

        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')

        L_parallel = self.input & Inductor()(self.L_parallel, **self.load_args) & self.output
