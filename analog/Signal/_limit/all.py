from skidl import Net
from bem.basic import Resistor, Diode

from PySpice.Unit import u_Ohm


class Modificator:
    #@subcircuit
    def circuit(self):
        super().circuit()

        R = Resistor()
        D = Diode(type='generic')

        signal = self.output
        self.output = Net('SignalLimitedOutput')

        limiter = signal & R(1000 @ u_Ohm) & self.output & (D() | D()) & self.v_ref
