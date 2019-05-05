from .. import Base
from bem import Resistor, Diode
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm

class Modificator(Base):
    #@subcircuit
    def circuit(self):
        super().circuit()

        R = Resistor()
        D = Diode()

        load = {
            'V': self.V,
            'Load': self.Load
        }
        
        signal = self.output
        self.output = Net('SignalLimitedOutput')

        limiter = signal & R(value=1000@u_Ohm) & self.output & (D(**load)['A', 'K'] | D(**load)['K', 'A']) & self.v_ref
