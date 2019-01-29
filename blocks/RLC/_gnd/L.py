from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_gnd = 1 @ u_H

    def __init__(self, L_gnd, *args, **kwargs):
        self.L_gnd = L_gnd
        
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('ParallelCapacitorOutput')

        L = Build('Inductor').block
        L_out = L(value=self.L_gnd, ref='L_g')

        circuit = signal & self.output & L_out['+,-'] & self.gnd