from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_vref = 1 @ u_H

    def willMount(self, L_vref):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('VrefInductorOutput')


        L_v_ref = Inductor()(self.L_vref, **self.load_args)

        circuit = self.v_ref & L_v_ref & self.output & signal
