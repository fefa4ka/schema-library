from .. import Base
from bem.basic import Resistor
from skidl import Net


class Modificator(Base):
    """
    This design inverts the input signal, V, and applies a signal gain of -Gain. The input signal typically
    comes from a low-impedance source because the input impedance of this circuit is determined by the
    input resistor, R_input. The common-mode voltage of an inverting amplifier is equal to the voltage connected to
    the non-inverting node, which is ground in this design.
    """

    def willMount(self, Gain=10):
        pass

    def circuit(self):
        R = Resistor()

        # Determine the starting value of R_input.
        # The relative size of R_input to the signal source impedance affects the
        # gain error. Assuming the impedance from the signal source is low (for example, 100 Ω), set R_input = 10 kΩ
        # for 1% gain error.
        source = R(self.R_load * 10)
        feedback = R(self.Gain * source.value)
        self.NG = 1 + feedback.value / source.value

        block_input = Net('InverterInput')
        block_input & source & self.input_n & feedback & self.output
        self.input & self.gnd
        self.input = block_input


