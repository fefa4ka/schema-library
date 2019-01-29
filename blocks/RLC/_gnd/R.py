from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_gnd = 1 @ u_Ohm

    def __init__(self, R_gnd, *args, **kwargs):
        self.R_gnd = R_gnd

        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('ParallelResistorOutput')

        R = Build('Resistor').block
        R_out = R(value=self.R_gnd, ref='R_g')

        circuit = signal & self.output & R_out['+,-'] & self.gnd