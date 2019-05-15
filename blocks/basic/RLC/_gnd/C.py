from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_gnd = 1 @ u_F

    def willMount(self, C_gnd):
        pass
        
    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('GndCapacitorOutput')

        C_out = Capacitor()(value=self.C_gnd, ref='C_g', **self.load_args)

        circuit = signal & self.output & C_out['+', '-'] & self.gnd