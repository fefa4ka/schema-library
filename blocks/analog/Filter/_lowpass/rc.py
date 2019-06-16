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

    f_3dB_low = 500000 @ u_Hz

    C_pass = 1e-6 @ u_F
    R_low = 1000 @ u_Ω

    def willMount(self, f_3dB_low=None):
        """
            f_3dB_low -- `f_(3db) = 1/(2πR_(series)C_(gnd))`
        """
        self.R_low = self.R_load / 10
        self.C_pass = 1 / (2 * pi * self.R_low * f_3dB_low) @ u_F
        self.tau = self.R_low * self.C_pass

    def network(self):
        return LSection(
            R('R_series'),
            C('C_gnd')
        )

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('FilterLowpassOutput')
        lowpass = RLC(series=['R'], gnd=['C'])(
            R_series = self.R_low,
            C_gnd = self.C_pass
        )

        self.output = lowpass.output
        lowpass.input += signal
        lowpass.gnd += self.gnd
