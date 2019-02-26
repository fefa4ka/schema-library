from .. import Base, Build
from skidl import Net, subcircuit
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

    def __init__(self, f_0=None, Q=None, C_gnd=None, *arg, **kwargs):
        self.f_0 = f_0

        # if C_gnd and L_gnd:

        f_0_value = None
        if f_0:
            f_0_value = f_0.value * f_0.scale

        self.C_gnd = C_gnd
        C_gnd_value = C_gnd.scale * C_gnd.value
        self.R_load = Q / (2 * pi * f_0_value * C_gnd_value) @ u_Ω

        self.L_gnd = pow(1 / (2 * pi * f_0_value * sqrt(C_gnd_value)), 2) @ u_H
        # if L_gnd:
        
        # if C_gnd:
        

        super().__init__(*arg, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalBandpassOutput')

        RLC = Build('RLC', series=['R'], gnd=['L', 'C']).block
        rlc = RLC(
            R_series = self.R_load,
            L_gnd = self.L_gnd,
            C_gnd = self.C_gnd
        )


        self.output = rlc.output
        rlc.input += signal
        rlc.gnd += self.gnd
