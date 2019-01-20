from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    @subcircuit
    def circuit(self):
        super().circuit()

        bridge_output = self.output
        self.output = Net('BridgeOutput')

        C = Build('Capacitor', **self.mods, **self.props).block
        
        C_value = self.I_load / (self.frequency * self.V_ripple)

        circuit = bridge_output & self.output & C(value=C_value @ u_F)['+', '-'] & self.output_gnd