from bem.basic import Resistor, Capacitor, Inductor
from bem import Net
from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt


class Modificator:
    """## RLC Bandpass Filter

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    def willMount(self, f_0_band = 5e5 @ u_Hz, Q_band=2, C_tank=1e-9 @ u_F):
        self.R_band = self.Q_band / (2 * pi * self.f_0_band * self.C_tank) @ u_Ω
        self.L_tank = pow(1 / (2 * pi * self.f_0_band * sqrt(self.C_tank)), 2) @ u_H
        self.tau = self.R_band * self.C_tank

    def circuit(self):
        super().circuit()

        output = Net('FilterBandpassOutput')

        # Sink resistor
        R_band = Resistor()(self.R_band)
        # Inductor tanker
        L_tank = Inductor()(self.L_tank)
        C_tank = Capacitor()(self.C_tank)

		# Filter Network
        self & R_band & output & (L_tank | C_tank) & self.gnd

        self.output = output
