from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_parallel = 1 @ u_Ohm

    def willMount(self, R_parallel):
        pass

    def circuit(self):
        super().circuit()

        if not (self.input and self.output):
            self.input = Net('RLCInput')
            self.output = Net('RLCOutput')

        R = Build('Resistor').block
        R_out = R(value=self.R_parallel, ref='R_p', **self.load_args)

        circuit = self.input & R_out['+,-'] & self.output