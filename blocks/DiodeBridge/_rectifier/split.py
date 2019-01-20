from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    output_inverse = None

    @subcircuit
    def circuit(self):
        super().circuit()
        
        self.output_inverse = self.output_gnd
        self.output_gnd = Net('BridgeOutputGround')

        C = Build('Capacitor', **self.mods, **self.props).block

        C_value = self.I_load / (self.frequency * self.V_ripple)

        circuit = self.output & C(value=C_value @ u_F)['+', '-'] & self.output_gnd & C(value=C_value @ u_F)['+', '-'] & self.output_inverse
