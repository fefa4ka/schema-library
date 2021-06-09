from math import log

from PySpice.Unit import u_A, u_F, u_Ohm, u_s, u_V, u_Hz
from .. import Base
from bem import u
from bem.basic import Resistor, Capacitor


class Modificator(Base):
    """## Simple RC Integrator
    The good news is that it works, sort of.
    The bad news is that the circuit is no longer a perfect integrator.
    That’s because the current through `C` (whose integral produces the output voltage) is no longer proportional to Vin; it is now proportional to the difference between `V_(i\\n)` and `V`.

    `V_(out)(t) = RC * (d/dt) * V_(in)(t)`

    ```
    vs = VS(flow='PULSEV')(V=10, Frequency=50)
    load = Resistor()(1000)
    integrator = Example()
    vs & integrator & load & vs

    watch = integrator
    ```


    * Paul Horowitz and Winfield Hill. "1.4.3 Differetiators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 25
    """



    def willMount(self, Frequency=50 @ u_Hz):
        pass

    # @subcircuit
    def circuit(self):
        period = 1 / self.Frequency
        quant = period / 4
        rate = self.V / quant

        self.tau = u(self.V / rate)

        # So we connect a resistor in series with the more usual integrator input voltage signal, to convert it to a current.
        discharger = Resistor()(self.R_load / 10)
        # Thus a simple capacitor, with one side grounded, is an integrator. The current through the capacitor `I_(i\n(t))=C*dV(t)/dt`.
        integrator = Capacitor()((self.tau / discharger.value) @ u_F)

        self.input & self.v_ref & discharger & self.output & integrator & self.gnd

