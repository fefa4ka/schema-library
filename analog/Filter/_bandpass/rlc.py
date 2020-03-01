from .. import Base
from bem.basic import RLC
from bem import Net
from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt

class Modificator(Base):
    """**LC Bandpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    f_0_band = 500000 @ u_Hz

    L_tank = 1e-8 @ u_H
    C_tank = 1e-6 @ u_F
    R_band = 1000 @ u_Ω
    Q_band = 2

    def willMount(self, f_0_band, Q_band, C_tank):
        self.R_band = Q_band / (2 * pi * f_0_band * C_tank) @ u_Ω
        self.L_tank = pow(1 / (2 * pi * f_0_band * sqrt(C_tank)), 2) @ u_H
        self.tau = self.R_band * self.C_tank

    def circuit(self):
        super().circuit()
        
        output = Net('FilterBandpassOutput')

        rlc = RLC(series=['R'], gnd=['L', 'C'])(
            R_series = self.R_band,
            L_gnd = self.L_tank,
            C_gnd = self.C_tank
        )

        signal = self & rlc & output
        self.output = output
