

from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical
from bem.basic import Diode, Resistor

class Base(Electrical()):
    def willMount(self, V_out=3.3 @ u_V):
        """
            P_zener -- The zener must be able to dissipate `P_(zen\er) =  ((V_(i\\n) - V_(out))/R_(i\\n) - I_(out)) * V_(out)`
            R_in -- Some current must flow through the zener, so you choose `(V_(i\\n)(min) - V_(out))/R_(i\\n) > I_(load)(max)`
        """
        self.load(V_out)

