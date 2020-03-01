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

        
        L_out = Inductor()(value=self.L_vref, ref='L_v', **self.load_args)

        circuit = signal & self.output & L_out['-,+'] & self.v_ref