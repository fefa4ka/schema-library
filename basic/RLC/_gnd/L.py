from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    def willMount(self, L_gnd=1 @ u_H):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('GndInductorOutput')

        L_gnd = signal & self.output & Inductor()(self.L_gnd) & self.gnd
