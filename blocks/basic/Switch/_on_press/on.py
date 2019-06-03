from .. import Base
from bem import Resistor
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A

class Modificator(Base):
    """**Transistor Switch**
 
    """

    def circuit(self):
        super().circuit()
    
        rc = self \
            & Resistor()(10000) \
                & Bipolar(
                    type='npn',
                    common='emitter'
                )(collector=self.load_block) & self.gnd