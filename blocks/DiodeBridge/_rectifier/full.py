from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Block):
    @subcircuit
    def create_circuit(self, R_load=None, V_out=None, V_ripple=1 @ u_V, I_load=1 @ u_A, P_load=None, frequency=220 @ u_Hz):
        instance = super().create_circuit()

        bridge_output = instance.output
        instance.output = Net('BridgeOutput')

        C = Build('Capacitor', **self.mods, **self.props).block

        if R_load and V_out:
            I_load = V_out / R_load
        
        C_value = I_load / (frequency * V_ripple)

        circuit = bridge_output & instance.output & C(value=C_value @ u_F)['+', '-'] & instance.output_gnd
    
        return instance
