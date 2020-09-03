from .. import Base
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from skidl import Net


class Modificator(Base):
    """
        ## Bipolar emitter follower power booster
        For high output current, a power transistor follower can be hung on an op-amp output.

        In this case a non-inverting amplifier has been drawn, though a follower can be added
        to any op-amp configuration.

        Notice that feedback is taken from the emitter; thus feedback enforces the desired output voltage
        in spite of the `V_(BE)` drop. This circuit has the usual problem that the follower output can only source current.


        * Paul Horowitz and Winfield Hill. "4.3.1 Linear circuits" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p.434 
    """
    def circuit(self):
        super().circuit()

        output = Net('BoostedOpAmp')
        boost = self & Bipolar(type='npn', common='emitter', follow='emitter')(
            emitter=Resistor()(self.V / self.I_load)
        ) & output
        self.output = output
