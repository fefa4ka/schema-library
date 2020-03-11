from bem.abstract import Electrical
from bem.basic import Resistor, OpAmp
from bem.analog.voltage import Divider
from bem import u_Hz, u_Ohm
from math import pi

class Modificator(Electrical()):
    """
    This design inverts the input signal, V, and applies a signal gain of -Gain. The input signal typically
    comes from a low-impedance source because the input impedance of this circuit is determined by the
    input resistor, R_input. The common-mode voltage of an inverting amplifier is equal to the voltage connected to
    the non-inverting node, which is ground in this design.
    """

    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }


    def willMount(self, Gain=2, Z_in=100 @ u_Ohm, frequency=100 @ u_Hz):
        self.load(self.V)

        self.slew_rate = 2 * pi * frequency * self.V * Gain * -1
        # Transfer function V_output = V_input * (- R_feedback / R_input)



    def circuit(self):
        R = Resistor()

        R_feedback = R(self.Z_in * 100)
        R_input = R(R_feedback.value / (self.Gain - 1))

        buffer = OpAmp()(frequency=self.frequency)

        buffer.v_ref & self.v_ref

        self.input & buffer.input
        buffer.gnd & self.v_inv

        self.gnd & R_input & buffer.input_n & R_feedback & buffer.output & self.output
