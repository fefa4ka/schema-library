from .. import Base

from bem import Net
from bem import u, u_Ω, u_F, u_Hz, u_Ohm
from bem.basic import Resistor, Capacitor 
from math import pi
from lcapy import LSection, R, C

class Modificator(Base):
    """## RC Lowpass Filter
    The circuit is called a lowpass filter, because it passes low frequencies and blocks high frequencies.

    If you think of it as a frequency-dependent voltage divider, this makes sense: the lower leg
    of the divider (the capacitor) has a decreasing reactance with increasing frequency,
    so the ratio of `V_(out)/V_(i\\n)` decreases accordingly:
    `V_(out) / V_(i\\n) ≈ X_C / (R + X_C) ≈ (1 / ωC) /  (R + 1 / ωC) ≈ 1 / (1 + ωC)`

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 50-51
    """

    def willMount(self, f_3dB_low=5e5 @ u_Hz, R_low = 0 @ u_Ohm, C_pass = 0 @ u_F):
        """
            f_3dB_low -- `f_(3db) = 1/(2πR_(series)C_(gnd))`
        """
        self.load(self.V)

    def network(self):
        return LSection(
            R('R_row'),
            C('C_pass')
        )

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('FilterLowpassOutput')

        if not self.R_low:
            self.R_low = self.R_load
            divider = signal & Resistor()(self.R_low) & self.output
        else:
            signal & self.output

        if not self.C_pass:
            self.C_pass = 1 / (2 * pi * self.R_low * self.f_3dB_low) @ u_F
            resonator = self.output & Capacitor()(self.C_pass) & self.gnd
        else:
            self.output & self.gnd

        self.tau = self.R_low * self.C_pass
