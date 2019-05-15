from .. import Base
from bem.basic import Transistor_Bipolar, Resistor

from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Base):
    """**NOT Gate — Inverter**
    
    Here a high voltage into the base will turn the transistor on, which will effectively connect the collector to the emitter. Since the emitter is connected directly to ground, the collector will be as well (though it will be slightly higher, somewhere around VCE(sat) ~ 0.05-0.2V). If the input is low, on the other hand, the transistor looks like an open circuit, and the output is pulled up to VCC

    """

    def circuit(self):
        super().circuit()
        signals = self.outputs

        new_outputs = []
        for signal in signals:
            inverted = Net('LogicInverted')
            inverter = Transistor_Bipolar(type='npn', common='emitter', follow='collector')(
                collector = Resistor()(1000),
                base = Resistor()(10000)
            )
            inverter.v_ref += self.v_ref
            inverter.gnd += self.gnd
            circuit = signal & inverter & inverted  

            new_outputs.append(inverted)
        
        self.outputs = new_outputs

        # For One line
        # inverted = Net('LogicInverted')
        # inverter = self & Resistor()(10000) & BJT(type='npn', common='emitter', follow='collector')(
        #     collector = Resistor()(1000) 
        # ) & inverted  

        # self.output = inverted