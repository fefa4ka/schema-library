from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm

class Modificator(Base):
    #@subcircuit
    def circuit(self):
        super().circuit()

        R = Build('Resistor').block
        D = Build('Diode').block
        
        signal = self.output
        self.output = Net('SignalLimitedOutput')

        limiter = signal & R(value=1000@u_Ohm) & self.output & (D()['A', 'K'] | D()['K', 'A']) & self.v_ref
