from bem.abstract import Electrical
from bem.basic import Resistor, OpAmp
from bem import u_Hz, u_Ohm
from math import pi


class Base(Electrical(port='many')):
    pins = {
        'input': True,
        'input_n': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    props = {
        'via': ['opamp', 'bipolar', 'mosfet']
    }

    def willMount(self, Gain=[2], Frequency=100 @ u_Hz):
        if type(Gain) == list and len(Gain) == 1:
            self.Gain = Gain[0]

    def circuit(self):
        R = Resistor()

        R_init = self.R_load * 10
        Gain = max(self.Gain) if type(self.Gain) == list else self.Gain
        # Determine the starting value of R_input.
        # The relative size of R_input to the signal source impedance affects the
        # gain error. Assuming the impedance from the signal source is low (for example, 100 Ω), set R_input = 10 kΩ
        # for 1% gain error.
        feedback = R(Gain * R_init)

        summer = OpAmp()(Frequency=self.Frequency)
        summer.v_ref & self.v_ref
        summer.input & self.gnd
        summer.v_inv & self.v_inv

        for index, signal in enumerate(self.inputs):
            Gain = self.Gain[index] if type(self.Gain) == list else self.Gain
            source = R(feedback.value / Gain)
            signal & source & summer.input_n

        summer.input_n & feedback & summer.output & self.output
