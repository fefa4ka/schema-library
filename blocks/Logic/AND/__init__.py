from .. import Base
from bem import Transistor_Bipolar, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Base):
    """**AND Gate**
    
    If either transistor is turned off, then the output at the second transistor’s collector will be pulled low. If both transistors are “on” (bases both high), then the output of the circuit is also high.

    """
    
    def circuit(self):
        super().circuit()

        signals = self.outputs
        
        v_ref = self.v_ref

        for signal in signals:

            and_input = Transistor_Bipolar(type='npn', follow='emitter')(
                collector = v_ref,
                base = Resistor()(10000)
            )
            and_input.input += signal
            v_ref = and_input.output
        
        self.outputs = [v_ref]

        pulldown = v_ref & Resistor()(10000) & self.gnd
