from .. import Base, Net
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_kOhm, u_A, u_V


class Modificator(Base):
    """**Digital Low-Current Switch **
    
    """

    def circuit(self):
        self.input = self.output = Net('DigitalInput')
        amplified = Net('DigitalAmplifiedInput')
        switch = self & Bipolar(
            type='npn',
            common='emitter',
            follow='emitter')(
                emitter=Resistor()(10 @ u_kOhm),
            ) & Resistor()(100 @ u_Ohm) & amplified
        
        self.output = amplified
        
        super().circuit()