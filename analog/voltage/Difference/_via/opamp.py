from .. import Base
from skidl import Net
from bem.basic import Resistor, OpAmp
from bem import Net, u, u_Ohm, u_V, u_A, u_kOhm

class Modificator(Base):
    """
    """
    pins = {
        'input': 'InputA',
        'output': True,
        'input_n': 'InputB',
        'output_n': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    V_ref = 10 @ u_V
    V_gnd = -10 @ u_V

    R_in = 0 @ u_Ohm
    R_feedback = 0 @ u_Ohm

    G_diff = 0
    G_cm = 0
    CMMR = 0

    gain = 10

    def willMount(self, gain):
        """
        """
        self.load(self.V)
        self.R_in = self.R_load * 10
        self.R_feedback = self.R_in * gain

        pass


    def circuit(self):
        R = Resistor()
        opamp = self.props.get('unit', None)
        if not opamp:
            opamp = OpAmp()(V=self.V_ref)

        input_p = self.input & R(self.R_in) & opamp.input
        input_n = self.input_n & R(self.R_in) & opamp.input_n

        sense = opamp.input & R(self.R_feedback) & opamp.output
        ref = opamp.input_n & R(self.R_feedback) & self.v_inv

        self.v_ref += opamp.v_ref
        self.v_inv += opamp.gnd

        self.output += opamp.output
