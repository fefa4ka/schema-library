from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_parallel = 1 @ u_F

    def __init__(self, C_parallel, *args, **kwargs):
        self.C_parallel = C_parallel

        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
            
        C = Build('Capacitor').block
        
        C_out = C(value=self.C_parallel, ref='C_p')

        circuit = self.input & C_out['+', '-'] & self.output