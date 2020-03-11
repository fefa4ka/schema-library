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
        self.R_in = (
            u(self.V - self.V_out)
            / u(self.I_load) / 2
        ) @ u_Ohm

        self.P_zener = ((self.V - self.V_out) / self.R_in - self.I_load) * self.V_out

        self.v_ref += self.input

        regulator = self.input \
                        & Resistor()(self.R_in, **self.load_args) \
                            & self.output \
                        & Diode(
                            type='zener',
                            BV=u(self.V_out),
                            **self.load_args
                        )(Load=self.Load, V=self.V,)['K, A'] \
                    & self.gnd

