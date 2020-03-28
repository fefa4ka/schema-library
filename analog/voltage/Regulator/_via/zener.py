from .. import Base
from bem.basic import Resistor, Diode
from bem.basic.transistor import Bipolar
from bem import u

from PySpice.Unit import u_Ohm, u_V, u_A, u_F, u_W

class Modificator(Base):
    """**Zener Voltage Regulator**
    
    The simplest regulated supply of voltage is simply a zener. Some current must flow through the zener.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83

    """

    def willMount(self):
        """
            P_zener -- The zener must be able to dissipate `P_(zen\er) =  ((V_(i\\n) - V_(out))/R_(i\\n) - I_(out)) * V_(out)`
            R_in -- Some current must flow through the zener, so you choose `(V_(i\\n)(min) - V_(out))/R_(i\\n) > I_(load)(max)`
        """
        pass

    def circuit(self, **kwargs):
        # The minimum value of the series resistor, R_in
        val = (self.V - self.V_out) / self.I_load / 10
        source = Resistor()((self.V - self.V_out) / self.I_load / 10)
        P_zener = ((self.V - self.V_out) / source.value - self.I_load) * self.V_out
        regulator = Diode(type='zener', BV=self.V_out, P=P_zener)()

        self.input & source & self.output & regulator['K, A'] & self.gnd


