from math import log

from PySpice.Unit import u_A, u_F, u_Ohm, u_s, u_V, u_Hz
from .. import Base
from bem import u
from bem.basic import Resistor, Capacitor


class Modificator(Base):
    """**Simple RC Differentiator**

    `V_(out)(t) = RC * (d/dt) * V_(in)(t)`

    * Paul Horowitz and Winfield Hill. "1.4.3 Differetiators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 25
    """



    def willMount(self, frequency=50 @ u_Hz):
        pass

    # @subcircuit
    def circuit(self):
        period = 1 / u(self.frequency)
        quant = period / 4
        rate = u(self.V) / quant

        self.RC = u(self.V) / rate

        self.R_out = self.R_load

        if not self.R_out:
            self.R_out = (self.RC / u(self.C_out)) @ u_Ohm

        if not hasattr(self, 'C_in'):
            self.C_in = (self.RC / u(self.R_out)) @ u_F

        C_in = Capacitor()(self.C_in)
        Current_sensing = Resistor()(self.R_out)

        self.input & self.v_ref & C_in & self.output & Current_sensing & self.gnd

