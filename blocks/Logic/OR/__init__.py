from .. import Base
from bem import Transistor_Bipolar, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Base):
    """**OR Gate**
    
    In this circuit, if either (or several) A or B are high, that respective transistor will turn on, and pull the output high. If both transistors are off, then the output is pulled low through the resistor.

    """
    
    def circuit(self):
        super().circuit()

        signals = self.outputs
        output = Net('LoginOrOutput')
        for signal in signals:
            or_input = Transistor_Bipolar(type='npn', common='emitter', follow='emitter')(
                collector = self.v_ref,
                base = Resistor()(10000),
                emitter = output
            )
            or_input.input += signal
            # or_input.emitter += output
        
        self.outputs = [output]

        pulldown = output & Resistor()(10000) & self.gnd
