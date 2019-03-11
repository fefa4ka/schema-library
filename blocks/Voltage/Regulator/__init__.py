from skidl import Net, subcircuit

from bem import (Block, Build, Diode, Resistor, is_tolerated, u, u_A, u_ms, u_W,
                 u_Ohm, u_s, u_V)
from settings import params_tolerance


class Base(Block):
    """**Voltage Regulator**
    
    The simplest regulated supply of voltage is simply a zener. Some current must flow through the zener.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83

    """

    V_in = 25 @ u_V
    V_out = 10 @ u_V
    P_zener = 0 @ u_W
    R_in = 0 @ u_Ohm

    def __init__(self, V_in=None, V_out=None, Load=None):
        """
            P_zener -- The zener must be able to dissipate `P_(zen\er) =  ((V_(i\\n) - V_(out))/R_(i\\n) - I_(out)) * V_(out)`
            R_in -- Some current must flow through the zener, so you choose `(V_(i\\n)(min) - V_(out))/R_(i\\n) > I_(load)(max)`
        """
        self.V_in = V_in
        self.V_out = V_out
        self.Load = Load 
        self.load(V_out)
        self.R_in = (
            u(self.V_in - self.V_out)
            / u(self.I_load) / 2
        ) @ u_Ohm
        self.P_zener = ((self.V_in - self.V_out) / self.R_in - self.I_load) * self.V_out
        self.circuit()
    
    def circuit(self, **kwargs):
        self.input = Net("VoltageRegulatorInput")
        self.output = Net("VoltageRegulatorOutput")
       
        self.v_ref = self.input
        self.gnd = Net()

        regulator = self.input \
                        & Resistor()(self.R_in) \
                            & self.output \
                        & Diode(
                            type='zener',
                            BV=u(self.V_out)
                        )()['K, A'] \
                    & self.gnd
