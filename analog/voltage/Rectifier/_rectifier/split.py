from .. import Base
from skidl import Net
from bem.basic import Capacitor

from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    def willMount(self, V_ripple=1 @ u_V, Frequency=5e5 @ u_Hz):
        """
            V_ripple -- Periodic variations in voltage about the steady value
            Frequency -- Input signal frequency
            C_ripple -- A relatively large value capacitor; it charges up to the peak output voltage during the diode conduction
        """
        pass

    def circuit(self):
        super().circuit()

        self.output_inverse = self.output_n
        self.output_n = Net('BridgeOutputGround')

        C = Capacitor(**self.mods, **self.props)
        self.C_ripple = self.I_load / (self.Frequency * self.V_ripple) @ u_F

        C_ripple_out = C(self.C_ripple)
        C_ripple_inv = C(self.C_ripple)

        circuit = self.output & C_ripple_out & self.output_n & C_ripple_inv & self.output_inverse
        self.output_inverse.fixed_name = False
