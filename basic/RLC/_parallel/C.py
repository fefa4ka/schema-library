from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    def willMount(self, C_parallel=1 @ u_F):
        pass

    def circuit(self):
        super().circuit()

        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')

        C_out = self.input & Capacitor()(self.C_parallel) & self.output
