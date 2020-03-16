from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    def willMount(self, L_vref=1 @ u_H):
        pass

    def circuit(self):
        super().circuit()
        signal = self.output
        self.output = Net('VrefInductorOutput')

        L_v_ref = self.v_ref & Inductor()(self.L_vref) & self.output & signal
