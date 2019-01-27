from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_parallel = 1 @ u_F

    def __init__(self, C_parallel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.C_parallel = C_parallel

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('ParallelCapacitorOutput')

        C = Build('Capacitor').block
        
        C_out = C(value=self.C_parallel, ref='C_p')

        circuit = signal & self.output & C_out['+', '-'] & self.gnd