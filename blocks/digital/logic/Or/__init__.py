from skidl import Net
from bem.abstract import Electrical, Network
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Network(port='many'), Electrical()):
    """
    **OR Gate**
    
    In this circuit, if either (or several) A or B are high, that respective transistor will turn on, and pull the output high. If both transistors are off, then the output is pulled low through the resistor.

    """
    
    def circuit(self):
        if len(self.inputs) == 0:
            return

        output = Net('LoginOrOutput')
        for signal in self.inputs:
            or_input = Bipolar(type='npn', common='emitter', follow='emitter')(
                collector = self.v_ref,
                base = Resistor()(10000),
                emitter = output
            )
            or_input.input += signal
            # or_input.emitter += output
        
        self.outputs = [output]

        pulldown = output & Resistor()(10000) & self.gnd
