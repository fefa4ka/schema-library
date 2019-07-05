from .. import Base
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

    gain = 1

    def willMount(self, gain):
        """
        G_diff -- `G_(di\\f\\f) = -R_c / (2*(r_e + R_e))`
        G_cm -- `G_(cm) = -R_c / (2 * R_(out) + R_e)` You can determine the _common-mode gain_ by putting identical signals v_in on both inputs. 
        CMMR -- A good differential amplifier has a high _common-mode rejection ratio_ `CM\\R\\R = R_1/(R_e + r_e)` the ratio of response for a normal-mode signal to the response for a common-mode signal of the same amplitude.
        """
        self.R_in = 25 @ u_kOhm
        self.R_feedback = self.R_in * gain

        pass
        

    def circuit(self):
        R = Resistor()
        opamp = self.props.get('unit', None)
        if not opamp:
            opamp = OpAmp()(V=self.V_ref).A

        input_p = self.input & R(self.R_in) & opamp.input 
        input_n = self.input_n & R(self.R_in) & opamp.input_n

        sense = opamp.input & R(self.R_feedback) & opamp.output
        ref = opamp.input_n & R(self.R_feedback) & self.v_inv

        self.v_ref += opamp.v_ref
        self.v_inv += opamp.gnd

        self.output += opamp.output

