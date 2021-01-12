from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A


class Modificator:
    """**Transistor Switch**
 
    """

    def circuit(self):
        super().circuit()
        
        rc = self \
            & Resistor()(10000) \
                & Bipolar(
                    type='pnp',
                    common='collector',
                    follow='collector'
                )(collector = self.load_block) & self.gnd
