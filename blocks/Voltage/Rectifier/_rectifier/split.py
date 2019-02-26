from .. import Base
from bem import Capacitor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    output_inverse = None
    C_ripple = 0.01 @ u_F

    V_out = 10 @ u_V
    V_ripple = 1 @ u_V

    R_load = 1000 @ u_Ohm
    I_load = 0 @ u_A
    frequency = 10 @ u_Hz

    def __init__(self, V_out=None, V_ripple=None, frequency=None, R_load=None, I_load=None):
        self.V_out = V_out
        self.V_ripple = V_ripple
        self.R_load = R_load
        self.I_load = I_load
        self.frequency = frequency

        if self.R_load and self.V_out:
            self.I_load = self.V_out / self.R_load
        
        self.circuit()

    def circuit(self):
        super().circuit()
        
        self.output_inverse = self.output_n
        self.output_n = Net('BridgeOutputGround')

        C = Capacitor(**self.mods, **self.props)

        self.C_ripple = C_value = self.I_load / (self.frequency * self.V_ripple) @ u_F

        circuit = self.output & C(value=self.C_ripple)['+', '-'] & self.output_n & C(value=self.C_ripple)['+', '-'] & self.output_inverse
