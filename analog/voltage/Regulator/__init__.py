

from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical
from bem.basic import Diode, Resistor

class Base(Electrical()):
    """
    """
    def willMount(self, V_out=3.3 @ u_V):
        self.load(V_out)

