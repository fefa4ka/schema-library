from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_gnd = 1 @ u_F

    def __init__(self, C_gnd, *args, **kwargs):
        self.C_gnd = C_gnd
        
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

        C = Build('Capacitor').block
        C_out = C(value=self.C_gnd, ref='C_g')

        circuit = signal & self.output & C_out['+', '-'] & self.gnd