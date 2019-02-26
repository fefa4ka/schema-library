from .. import Base
from bem import Transistor_Bipolar, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A

class Modificator(Base):
    """**Transistor Switch**
 
    """

    def circuit(self):
        super().circuit()
    
        rc = self \
            & Resistor()(value=10000) \
                & Transistor_Bipolar(
                    type='npn',
                    common='emitter'
                )(collector=self.load)

        self.output = self.load.output