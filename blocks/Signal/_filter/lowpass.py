from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ω, u_F, u_Hz
from math import pi

class Modificator(Base):
    """**RC Lowpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 50-51
    """

    f_3dB = 20 @ u_Hz

    R_load = 1000 @ u_Ω
    C_gnd = 1e-6 @ u_F
    R_series = 1000 @ u_Ω

    def __init__(self, R_load=None, f_3dB=None, *arg, **kwargs):
        self.f_3dB = f_3dB
        f_3dB_value = f_3dB.value * f_3dB.scale
        R_series_value = (self.R_load.value * self.R_load.scale) / 10
        self.R_load = R_load
        self.R_series = R_series_value @ u_Ω
        self.C_gnd= 1 / (2 * pi * R_series_value * f_3dB_value) @ u_F

        super().__init__(*arg, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalLowpassOutput')
        RLC = Build('RLC', series=['R'], gnd=['C']).block
        rlc = RLC(
            R_series = self.R_series,
            C_gnd = self.C_gnd
        )

        self.output = rlc.output
        rlc.input += signal
        rlc.gnd += self.gnd
