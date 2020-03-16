from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    def willMount(self, C_vref=1 @ u_F):
       pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('VrefCapacitorOutput')

        C_v_ref = self.v_ref & Capacitor()(self.C_vref) & self.output & signal
