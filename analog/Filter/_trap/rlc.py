from .. import Base
from bem.basic import Resistor, RLC
from bem import u
from skidl import Net
from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt

class Modificator(Base):
    """**LC Bandpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    def willMount(self, f_0_trap=5e5 @ u_Hz, Q_trap=2, C_notch=1e-6 @ u_F):
        self.R_trap = Q_trap / (2 * pi * f_0_trap * C_notch) @ u_Ω

        self.L_notch = pow(1 / (2 * pi * f_0_trap * sqrt(C_notch)), 2) @ u_H
        self.tau = self.R_trap * self.C_notch

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('FilterTrapOutput')

        rin = Resistor()(value=self.R_trap, ref='R_in')
        lc = RLC(series=['L', 'C'])(
            L_series = self.L_notch,
            C_series = self.C_notch
        )
        lc.output += self.gnd

        circuit = signal & rin & (self.output | lc.input)

