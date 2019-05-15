from .. import Base
from bem.basic import Resistor, Capacitor
from bem import Net, u_Ohm, u_V
from math import pi


class Modificator(Base):
    """
    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 84
    """

    def willMount(self):
        self.R_e = 1000 @ u_Ohm
        self.V_drop += self.R_e * (self.V_ref / self.R_e)
      
    def ref(self):
        ref = Net('Reference')
        
        line = self.input & Resistor()(self.R_e, ref='R_e') & ref
        
        return ref
