from .. import Base
from bem import BJT, Resistor, Capacitor, RLC, SchmittTrigger
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Base):
    """**Abrupt Translation**

    Pulse width abrupt rise and fall
    """

    def circuit(self):
        super().circuit()

        # signal = self.output
        
        
        abrupt_translation = SchmittTrigger()()
        signal = self & abrupt_translation
        # self.output = Net('onHightAbruptPulse')x
        self.output = abrupt_translation.output



    