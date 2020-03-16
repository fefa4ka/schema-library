from bem.abstract import Electrical
from bem.basic import Resistor, OpAmp
from bem import u_Hz, u_Ohm
from math import pi

class Base(Electrical()):
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

    props = {
        'via': ['opamp', 'bipolar', 'mosfet']
    }

    def willMount(self, Gain=2, Frequency=100 @ u_Hz):
        self.slew_rate = 2 * pi * Frequency * self.V * Gain * -1
        # Transfer function V_output = V_input * (- R_feedback / R_input)

    def circuit(self):
        R = Resistor()

        # Determine the starting value of R_input.
        # The relative size of R_input to the signal source impedance affects the
        # gain error. Assuming the impedance from the signal source is low (for example, 100 Ω), set R_input = 10 kΩ
        # for 1% gain error.
        source = R(self.R_load * 10)
        feedback = R(self.Gain * source.value)
        self.NG = 1 + feedback.value / source.value

        inverter = OpAmp(boost='bipolar')(frequency=self.Frequency)

        inverter.v_ref & self.v_ref
        inverter.input & self.gnd
        inverter.gnd & self.v_inv

        self.input & source & inverter.input_n & feedback & inverter.output & self.output
