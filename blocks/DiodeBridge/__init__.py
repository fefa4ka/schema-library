from bem import Block
from skidl import Net, subcircuit
from PySpice.Unit import u_ms

"""Diode Bridge

    wave = half | full
    rectifier = full | split

    Power = Build('Power').block
    DiodeBridge = Build('DiodeBridge', wave='full', rectifier='split').block

    VCC = Power(source=SINEV(amplitude=10@u_V, frequency=100@u_Hz))
    bridge = DiodeBridge(V_ripple = 0.01 @ u_V, frequency=100 @ u_Hz, R_load=600 @ u_Ohm, V_out = 10 @ u_V)
    bridge.output_gnd += gnd
    rc = VCC & bridge & divider  & gnd

"""

class Base(Block):
    output_gnd = None
        
    def __series__(self, instance):
        if self.output and instance.input:
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            self.output += instance.input
        
        if self.output_gnd and instance.gnd:
            self.output_gnd += instance.gnd
        
        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref

    @subcircuit
    def create_circuit(self, **kwargs):
        instance = self.clone

        instance.input = Net("BridgeVoltage")
        instance.gnd = Net()
        instance.output = Net("BridgeOutput")
        instance.output_gnd = Net()
        
        instance.create_bridge()

        return instance