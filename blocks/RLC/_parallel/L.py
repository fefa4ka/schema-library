from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_parallel = 1 @ u_H

    def __init__(self, L_parallel, *args, **kwargs):
        self.L_parallel = L_parallel
        
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('ParallelInductorOutput')

        L = Build('Inductor').block
        
        L_out = L(value=self.L_parallel, ref='L_p')

        circuit = signal & self.output & L_out['+,-'] & self.gnd