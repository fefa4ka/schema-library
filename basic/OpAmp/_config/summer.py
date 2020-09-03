from .. import Base
from bem.abstract import Network
from bem.basic import Resistor
from skidl import Net


class Modificator(Base, Network(port='many')):
    def willMount(self, Gain=[2]):
        if type(Gain) == list and len(Gain) == 1:
            self.Gain = Gain[0]

    def circuit(self):
        super().circuit()

        R = Resistor()
        # Determine the starting value of R_input.
        # The relative size of R_input to the signal source impedance affects the
        # gain error. Assuming the impedance from the signal source is low (for example, 100 Ω), set R_input = 10 kΩ
        # for 1% gain error.
        R_init = self.R_load * 10
        Gain = max(self.Gain) if type(self.Gain) == list else self.Gain
        feedback = R(Gain * R_init)

        self.input & self.gnd

        print('summer', self.inputs)
        for index, signal in enumerate(self.inputs):
            Gain = self.Gain[index] if type(self.Gain) == list else self.Gain
            source = R(feedback.value / Gain)
            signal & source & self.input_n

        self.input_n & feedback & self.output & self.output

        # Second input, opamp input_n used for feedback
        self.input_n = Net('SummerSecondInput')

