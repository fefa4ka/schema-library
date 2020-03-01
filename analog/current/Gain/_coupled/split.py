from .. import Base
from bem.basic import Resistor, Capacitor
from bem import Net, u, u_F, u_Hz
from math import pi


class Modificator(Base):
    """**Split Supply**
 
    Because signals often are “near ground” it is convenient to use symmetrical positive and negative supplies. This simplifies biasing and eliminates coupling capacitors.

    Warning: you must always provide a dc path for base bias current, even if it goes only to ground. In this circuit it is assumed that the signal source has a dc path to ground. If not (e.g., if the signal is capacitively coupled), you must pro- vide a resistor to ground. `R_b` could be about one-tenth of `β * R_e`, as before.

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 84
    """

    def circuit(self):
        self.input_n = Net('ACGainSplitN')
        
        super().circuit()
