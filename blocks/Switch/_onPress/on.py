from .. import Base
from bem import BJT, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A

class Modificator(Base):
    """**Transistor Switch**
 
    """

    def circuit(self):
        amplifier = BJT(type='npn', common='emitter')(
            collector=self.load
        )
    
        self.output_n += self.load.output

        rc = self.input \
            & Resistor()(value=10000) \
            & amplifier

        super().circuit()

        amplifier.gnd += self.gnd
        amplifier.v_ref += self.v_ref