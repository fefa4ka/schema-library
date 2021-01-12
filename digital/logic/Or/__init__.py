from skidl import Net
from bem.abstract import Electrical
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A


class Base(Electrical(port='many')):
    """
    **OR Gate**

    In this circuit, if either (or several) A or B are high, that respective transistor will turn on, and pull the output high. If both transistors are off, then the output is pulled low through the resistor.

    """

    def circuit(self):
        for signal in self.inputs:
            or_gate = Bipolar(
                type='npn',
                common='emitter',
                follow='emitter'
            )(
                collector = self.v_ref,
                base = Resistor()(10000),
                emitter = self.output
            )
            signal & or_gate.input

        pulldown = self.output & Resistor()(10000) & self.gnd
