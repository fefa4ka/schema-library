from .. import Base
from bem.basic import Resistor, RLC
from bem import u

from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt

class Modificator(Base):
    """**LC Bandpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    f_0 = 1000 @ u_Hz

    R_in = 1000 @ u_Ω
    L_series = 1e-8 @ u_H
    C_series = 1e-6 @ u_F
    R_in = 1000 @ u_Ω
    Q = 2

    def willMount(self, f_0, Q, C_series):
        self.R_in = Q / (2 * pi * f_0 * C_series) @ u_Ω

        self.L_series = pow(1 / (2 * pi * f_0 * sqrt(C_series)), 2) @ u_H
        
    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalTrapOutput')

        rin = Resistor()(value=self.R_in, ref='R_in')
        lc = RLC(series=['L', 'C'])(
            L_series = self.L_series,
            C_series = self.C_series
        )
        lc.output += self.gnd

        circuit = signal & rin & (self.output | lc.input)
       