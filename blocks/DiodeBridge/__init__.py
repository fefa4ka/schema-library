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

    output_gnd = None
    V_out = 10 @ u_V
    V_ripple = 1 @ u_V

    R_load = 0 @ u_Ohm
    I_load = 0 @ u_A
    P_load = 0 @ u_W
    frequency = 220 @ u_Hz
    
    def __init__(self, V_out=None, V_ripple=None,  frequency=None, R_load=None, I_load=None, P_load=None):
        if self.R_load and self.V_out:
            self.I_load = self.V_out / self.R_load
        
        self.circuit()

    def __series__(self, instance):
        if self.output and instance.input:
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            self.output += instance.input
        
        if self.output_n and instance.input_n:
            self.output_n += instance.input_n
        
        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref

    #@subcircuit
    def circuit(self, **kwargs):
        self.input = Net("BridgeVoltage")
        self.gnd = Net()
        self.input_n = Net()
        self.output = Net("BridgeOutput")
        self.output_n = Net()
        
        self.create_bridge()