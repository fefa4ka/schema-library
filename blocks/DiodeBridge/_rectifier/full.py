from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    C_ripple = 0.01 @ u_F

    @subcircuit
    def circuit(self):
        super().circuit()

        bridge_output = self.output
        self.output = Net('BridgeOutput')

        C = Build('Capacitor', **self.mods, **self.props).block
        
        self.C_ripple = self.I_load / (self.frequency * self.V_ripple)  @ u_F

        circuit = bridge_output & self.output & C(value=self.C_ripple)['+', '-'] & self.output_gnd