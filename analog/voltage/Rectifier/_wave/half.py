from bem.basic import Diode
from .. import Base


class Modificator(Base):
    """
    ## Half-Wave Rectifier

    For a sinewave input that is much larger than the forward drop (about 0.6 V for silicon diodes, the usual type). This circuit is called a half-wave rectifier, because only half of the input waveform is used.
    """

    def create_bridge(self):
        bridge = self.input & Diode(type='generic')() & self.output

    def circuit(self, **kwargs):
        super().circuit(**kwargs)

        self.output_n = self.input_n = self.gnd
