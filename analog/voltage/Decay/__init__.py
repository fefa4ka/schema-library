from math import log

from PySpice.Unit import u_A, u_F, u_Ohm, u_s, u_V

from bem.abstract import Electrical
from bem.basic import Resistor, Capacitor


class Base(Electrical()):
    """**Decay to equilibrium**

    The product RC is called the time constant of the circuit. For `R_s` in ohms and `C_g` in farads, the product RC is in seconds. A `C_g` microfarad across `R_s` 1.0k has a time constant Time_to_`V_(out)` of 1 ms; if the capacitor is initially charged to `V_(out) = 1.0 V`, the initial current `I_(out)` is 1.0 mA.

    At time `t = 0`, someone connects the battery. The equation for the circuit is then

    `I = C * (dV) / (dT) = (V_(i\\n) - V_(out)) / R_s`

    with solution

    `V_(out) = V_(i\\n) + A * e ^ (-t / (R_s * C_g))`

    The constant `A` is determined by initial conditions: `V_(out) = 0` at `t = 0`; therefore, `A = −V_(i\\n)`, and

    `V_(out) = V_(i\\n) * (1 − e ^ (−t / (R_s * C_g)))`

    Once again there’s good intuition: as the capacitor charges up, the slope (which is proportional to current, because it’s a capacitor) is proportional to the remaining voltage (because that’s what appears across the resistor, producing the current); so we have a waveform whose slope decreases proportionally to the vertical distance it has still to go an exponential.

    To figure out the time required to reach a voltage `V_(out)` on the way to the final voltage `V_(i\\n)`: 

    `t = R * C * log_e(V_(i\\n) / (V_(i\\n) - V_(out)))`

    * Paul Horowitz and Winfield Hill. "1.4.2 RC circuits: V and I versus time" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 21-23
    """

    def willMount(self, V_out=5 @ u_V, Time_to_V_out=5e-3 @ u_s, reverse=False):
        """
            reverse -- Reverse capacitor connection
        """
        self.load(self.V)

    # @subcircuit
    def circuit(self):
        self.R_in = self.R_load / 10

        self.C_out = (self.Time_to_V_out / (self.R_in * log(self.V / (self.V - self.V_out)))) @ u_F

        current_source = Resistor()(self.R_in)
        discharger = Capacitor()(self.C_out)

        if self.reverse:
            self.input & current_source & self.output
            self.gnd & discharger & self.output
        else:
            self.input & current_source & self.output & discharger & self.gnd
