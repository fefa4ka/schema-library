from .. import Base
from bem.basic import RLC
from bem import Net
from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt

class Modificator(Base):
    """**LC Bandpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    f_0 = 1000 @ u_Hz

    R_load = 1000 @ u_Ω
    L_gnd = 1e-8 @ u_H
    C_gnd = 1e-6 @ u_F
    R_series = 1000 @ u_Ω
    Q = 2

    def willMount(self, f_0, Q, C_gnd):
        self.R_series = Q / (2 * pi * f_0 * C_gnd) @ u_Ω
        self.L_gnd = pow(1 / (2 * pi * f_0 * sqrt(C_gnd)), 2) @ u_H

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalBandpassOutput')

        rlc = RLC(series=['R'], gnd=['L', 'C'])(
            R_series = self.R_series,
            L_gnd = self.L_gnd,
            C_gnd = self.C_gnd
        )

        self.output = rlc.output
        rlc.input += signal
        rlc.gnd += self.gnd
