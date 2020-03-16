from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    def willMount(self, C_parallel=1 @ u_F):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('RLCOutput')

        C_parallel = signal & Capacitor()(self.C_parallel) & self.output
