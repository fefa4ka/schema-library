from bem.abstract import Electrical
from bem.basic import Resistor, OpAmp
from bem.analog.voltage import Divider
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
        'via': ['opamp', 'bipolar', 'mosfet'],
        'supply': ['single']
    }

    def willMount(self, Gain=2, Z_in=100 @ u_Ohm, frequency=100 @ u_Hz):
        self.load(self.V)

        self.slew_rate = 2 * pi * frequency * self.V * Gain * -1
        # Transfer function V_output = V_input * (- R_feedback / R_input)



    def circuit(self):
        R = Resistor()

        # Determine the starting value of R_input.
        # The relative size of R_input to the signal source impedance affects the
        # gain error. Assuming the impedance from the signal source is low (for example, 100 Ω), set R_input = 10 kΩ
        # for 1% gain error.
        R_input = R(self.Z_in * 100)
        R_feedback = R(self.Gain * R_input.value)
        self.NG = 1 + R_feedback.value / R_input.value

        buffer = OpAmp()(**self.load_args, frequency=self.frequency)

        buffer.v_ref & self.v_ref
        if 'single' in self.props.get('supply', []):
            split_power = Divider(type='resistive')(
                V=self.V,
                V_out=self.V / 2,
                Load=R_input.value)
            self.v_ref & split_power & buffer
            buffer.gnd & self.gnd & split_power.gnd
        else:
            buffer.input & self.gnd
            buffer.gnd & self.v_inv

        self.input & R_input & buffer.input_n & R_feedback & buffer.output & self.output
