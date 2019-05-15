from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_vref = 1 @ u_F

    def willMount(self, C_vref):
       pass
        
    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('VrefCapacitorOutput')

        C_out = Capacitor()(value=self.C_vref, ref='C_v', **self.load_args)

        circuit = signal & self.output & C_out['+', '-'] & self.v_ref