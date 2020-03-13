from bem.abstract import Electrical
from bem.basic import Resistor, Capacitor, OpAmp
from bem.analog.voltage import Divider
from bem import u_Hz, u_Ohm, u_kOhm, u_F
from math import pi

class Modificator(Electrical()):
    """
        The differentiator circuit outputs the derivative of the input signal over a frequency range based on the
        circuit time constant and the bandwidth of the amplifier. The input signal is applied to the inverting input so
        the output is inverted relative to the polarity of the input signal. The ideal differentiator circuit is
        fundamentally unstable and requires the addition of an input resistor, a feedback capacitor, or both, to be
        stable. The components required for stability limit the bandwidth over which the differentiator function is
        performed.

        * http://www.ti.com/lit/an/sboa276a/sboa276a.pdf
    """

    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, gain=1, Frequency=1e3 @ u_Hz):
        pass

    def circuit(self):
        """
        """
        R = Resistor()

        # Set R_input to a large standard value
        feedback = R(499 @ u_kOhm)
        # Set the minimum differentiation frequency at least half a decade below the minimum operating frequency.
        differentiator = Capacitor()((3.5 / (2 * pi * feedback.value * self.Frequency)) @ u_F)
        # Set the upper cutoff frequency at least half a decade above the maximum operating frequency
        sensor = R((1 / (3.5 * 2 * pi * differentiator.value * self.Frequency)) @ u_Ohm)

        self.tau = feedback.value * differentiator.value

        # Calculate the necessary op amp gain bandwidth product (GBP) for the circuit to be stable
        buffer = OpAmp()(frequency=self.Frequency)

        buffer.v_ref & self.v_ref
        buffer.gnd & self.v_inv

        self.input & differentiator & sensor & buffer.input_n & feedback & buffer.output & self.output
        self.gnd & buffer.input
