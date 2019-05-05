from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_vref = 1 @ u_Ohm

    def willMount(self, R_vref):
        pass

    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('VrefResistorOutput')

        R = Build('Resistor').block
        R_out = R(value=self.R_vref, ref='R_v', **self.load_args)

        circuit = signal & self.output & R_out['+,-'] & self.v_ref