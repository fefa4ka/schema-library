from .. import Base
from bem.basic import Capacitor

from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    output_inverse = None
    C_ripple = 0.01 @ u_F

    
    V_ripple = 1 @ u_V

    frequency = 10 @ u_Hz

    def willMount(self, V_ripple=None, frequency=None):
        """
            V_ripple -- Periodic variations in voltage about the steady value
            frequency -- Input signal frequency
            C_ripple -- A relatively large value capacitor; it charges up to the peak output voltage during the diode conduction
        """
        pass       

    def circuit(self):
        super().circuit()
        
        self.output_inverse = self.output_n
        self.output_n = Net('BridgeOutputGround')

        C = Capacitor(**self.mods, **self.props)
        self.C_ripple = C_value = self.I_load / (self.frequency * self.V_ripple) @ u_F
        C_ripple = {
             **self.load_args,
             'value': self.C_ripple,
             'ref': 'C_ripple'
        }

        circuit = self.output & C(**C_ripple)['+', '-'] & self.output_n & C(**C_ripple)['+', '-'] & self.output_inverse
