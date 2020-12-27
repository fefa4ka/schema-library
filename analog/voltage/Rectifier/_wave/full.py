from bem.basic import Diode
from .. import Base

class Modificator(Base):
    """
        ## Full-Wave Bridge

        The entire input waveform is used.

        The gaps at zero voltage occur because of the diodes’ forward voltage drop.

    """

    def create_bridge(self):
        D = Diode(type='generic')

        left = (D()['A,K'] & self.input & D()['A,K'])
        right = (D()['A,K'] & self.input_n & D()['A,K'])

        self.gnd & self.output_n & (left | right) & self.output


