from bem.basic import Diode
from .. import Base

class Modificator(Base):
    """
        **Full-Wave Bridge**

        The entire input waveform is used.

        The gaps at zero voltage occur because of the diodes’ forward voltage drop.

    """

    def create_bridge(self):
        def D(ref):
            return Diode(type='generic')(ref='D_' + ref, V=self.V_out, Load=self.Load)

        circuit = self.output_n & (
            (D('out_n_in')['A,K'] & self.input & D('in_out')['A,K'])
            | (D('out_n_in_n')['A,K'] & self.input_n & D('in_n_out')['A,K'])
        ) & self.output


