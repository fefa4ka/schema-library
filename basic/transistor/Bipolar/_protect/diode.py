from .. import Base
from bem.basic import Diode

class Modificator(Base):
    """**Base-emitter breakdown**

    A diode prevents base–emitter reverse voltage breakdown.

    Always remember that the base–emitter reverse breakdown voltage for silicon transistors is small, quite often as little as 6 volts. Input swings large enough to take the transistor out of conduction can easily result in breakdown (causing permanent degradation of current gain β) unless a protective diode is added.
    
    * Paul Horowitz and Winfield Hill. "2.2.3 Emitter follower" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82
 
    """

    def circuit(self):
        super().circuit()
        
        protect = self.emitter & Diode()()['A,K'] & self.base
        