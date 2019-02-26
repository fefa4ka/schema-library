from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_ms, u_Ohm, u_A, u_V, u_Hz, u_W


class Base(Block):
    """**Diode Bridge**
    
    A diode bridge is an arrangement of four (or more) diodes in a bridge circuit configuration that provides the same polarity of output for either polarity of input.

    
    """

    mods = {
        'wave': ['full']
    }

    def __series__(self, instance):
        if self.output and instance.input:
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            self.output += instance.input
        
        if self.output_n and instance.input_n:
            self.output_n += instance.input_n
        
        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref

    def circuit(self, **kwargs):
        self.input = Net("BridgeVoltage")
        self.gnd = Net()
        self.input_n = Net()
        self.output = Net("BridgeOutput")
        self.output_n = Net()
        
        self.create_bridge()
