from .. import Base

from bem.basic import Resistor, Capacitor
from bem import Net
from PySpice.Unit import u_Ω, u_F, u_Hz
from math import pi
from lcapy import LSection, R, C

class Modificator(Base):
    """**RC Highpass Filter**

    We’ve seen that by combining resistors with capacitors it is possible to make frequency-dependent voltage dividers, owing to the 
    frequency dependence of a capacitor’s impedance `Z_c = −j/(ωC)`. 
    Such circuits can have the desirable property of passing signal frequencies of interest while rejecting undesired signal frequencies.

    Engineers like to refer to the −3 dB “breakpoint” of a filter (or of any circuit that behaves like a filter). 
    In the case of the simple RC high-pass filter, the −3 dB breakpoint is given by `f_(3dB) = 1/(2πRC)`

    The impedance of a load driven by it should be much larger than `R_(gnd)` in order to prevent circuit loading effects 
    on the filter’s output, and the driving source should be able to drive a `R_(gnd)` load without significant attenuation (loss of signal amplitude)
    in order to prevent circuit loading effects by the filter on the signal source.

    * Paul Horowitz and Winfield Hill. "1.7.8 RC highpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 48-49
    """

    def willMount(self, f_3dB_high=5e5 @ u_Hz):
        self.load(self.V)
        self.R_shunt = self.R_load
        self.C_block = 1 / (2 * pi * self.R_shunt * f_3dB_high) @ u_F
        self.tau = self.R_shunt * self.C_block

    def network(self):
        return LSection(
            C('C_block'),
            R('R_shunt')
        )

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('FilterHighpassOutput')

        high_pass = signal & Capacitor()(self.C_block) & self.output & Resistor()(self.R_shunt) & self.gnd
