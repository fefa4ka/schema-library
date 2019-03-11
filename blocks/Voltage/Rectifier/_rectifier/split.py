from .. import Base
from bem import Capacitor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    output_inverse = None
    C_ripple = 0.01 @ u_F

    V_out = 10 @ u_V
    V_ripple = 1 @ u_V

    frequency = 10 @ u_Hz

    def __init__(self, V_out=None, V_ripple=None, frequency=None, Load=None):
        """
            V_ripple -- Periodic variations in voltage about the steady value
            frequency -- Input signal frequency
        """
        self.V_out = V_out
        self.V_ripple = V_ripple
        self.Load = Load
        self.load(self.V_out)
        self.frequency = frequency

        self.circuit()

    def circuit(self):
        super().circuit()
        
        self.output_inverse = self.output_n
        self.output_n = Net('BridgeOutputGround')

        C = Capacitor(**self.mods, **self.props)

        self.C_ripple = C_value = self.I_load / (self.frequency * self.V_ripple) @ u_F

        circuit = self.output & C(value=self.C_ripple)['+', '-'] & self.output_n & C(value=self.C_ripple)['+', '-'] & self.output_inverse
