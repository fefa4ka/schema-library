from .. import Base

from bem import Net
from bem import u, u_Ω, u_F, u_Hz
from bem.basic import RLC
from math import pi
from lcapy import LSection, R, C

class Modificator(Base):
    """**RC Lowpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 50-51
    """

    f_3dB = 20 @ u_Hz

    C_gnd = 1e-6 @ u_F
    R_series = 1000 @ u_Ω

    def willMount(self, f_3dB=None):
        self.R_series = self.R_load / 10
        self.C_gnd = 1 / (2 * pi * self.R_series * f_3dB) @ u_F

    def network(self):
        return LSection(
            R('R_series'),
            C('C_gnd')
        )

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalLowpassOutput')
        rlc = RLC(series=['R'], gnd=['C'])(
            R_series = self.R_series,
            C_gnd = self.C_gnd
        )

        self.output = rlc.output
        rlc.input += signal
        rlc.gnd += self.gnd