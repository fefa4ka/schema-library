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

    def willMount(self, Frequency=50 @ u_Hz):
        pass

    def circuit(self):
        period = 1 / self.Frequency
        quant = period / 4
        rate = self.V / quant

        self.tau = u(self.V / rate)

        current_sensing = Resistor()(self.R_load / 10)
        differetiator = Capacitor()((self.tau / current_sensing.value) @ u_F)

        self.input & self.v_ref & differetiator & self.output & current_sensing & self.gnd

