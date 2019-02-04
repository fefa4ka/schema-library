from .. import Base
from bem import Capacitor
from skidl import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_vref = 1 @ u_F

    def __init__(self, C_vref, *args, **kwargs):
        self.C_vref = C_vref
        
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('VrefCapacitorOutput')

        C_out = Capacitor()(value=self.C_vref, ref='C_g')

        circuit = signal & self.output & C_out['+', '-'] & self.v_ref