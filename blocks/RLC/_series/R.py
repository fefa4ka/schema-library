from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_series = 1 @ u_Ohm

    def willMount(self, R_series):
        pass

    def circuit(self):
        super().circuit()
    
        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('SeriesResistorOutput')
        
        R = Build('Resistor').block
        
        R_out = R(value=self.R_series, ref='R_s', **self.load_args)
        
        circuit = signal & R_out['+,-'] & self.output