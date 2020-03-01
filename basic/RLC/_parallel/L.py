from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_parallel = 1 @ u_H

    def willMount(self, L_parallel):
        pass
        
    def circuit(self):
        super().circuit()

        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')

        
        
        L_out = Inductor()(value=self.L_parallel, ref='L_p', **self.load_args)

        circuit = self.input & L_out & self.output
