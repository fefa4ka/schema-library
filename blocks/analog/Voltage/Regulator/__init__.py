

from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical
from bem.basic import Diode, Resistor

class Base(Electrical()):
    """**Voltage Regulator**
    
    The simplest regulated supply of voltage is simply a zener. Some current must flow through the zener.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83

    """

    V = 25 @ u_V
    V_out = 10 @ u_V
    P_zener = 0 @ u_W
    R_in = 0 @ u_Ohm

    def willMount(self, V_out=None):
        """
            P_zener -- The zener must be able to dissipate `P_(zen\er) =  ((V_(i\\n) - V_(out))/R_(i\\n) - I_(out)) * V_(out)`
            R_in -- Some current must flow through the zener, so you choose `(V_(i\\n)(min) - V_(out))/R_(i\\n) > I_(load)(max)`
        """
        self.load(V_out)
        self.R_in = (
            u(self.V - self.V_out)
            / u(self.I_load) / 2
        ) @ u_Ohm
        self.P_zener = ((self.V - self.V_out) / self.R_in - self.I_load) * self.V_out
    
    def circuit(self, **kwargs):
        self.input = Net("VoltageRegulatorInput")
        self.output = Net("VoltageRegulatorOutput")
       
        self.v_ref = self.input
        self.gnd = Net()

        regulator = self.input \
                        & Resistor()(self.R_in, **self.load_args) \
                            & self.output \
                        & Diode(
                            type='zener',
                            BV=u(self.V_out),
                            **self.load_args
                        )(Load=self.Load, V=self.V,)['K, A'] \
                    & self.gnd
