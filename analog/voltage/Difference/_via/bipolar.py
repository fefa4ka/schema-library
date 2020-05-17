from .. import Base
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from bem import Net, u, u_Ohm, u_V, u_A

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

    def willMount(self, V_inv=-10 @ u_V):
        """
        R_c -- `R_c = V_c / I_(quiescent)`
        R_e -- Hardcoded value `R_e = 1000 Ω`
        R_out -- Value is chosen to set the transistor’s emitters as close to 0 V as possible. Value is found by adding both the right and left branch’s. `R_(out) = (0V - V_(gnd)) / (2 * I_(quiescent))`
        G_diff -- `G_(di\\f\\f) = -R_c / (2*(r_e + R_e))`
        G_cm -- `G_(cm) = -R_c / (2 * R_(out) + R_e)` You can determine the _common-mode gain_ by putting identical signals v_in on both inputs.
        CMMR -- A good differential amplifier has a high _common-mode rejection ratio_ `CM\\R\\R = R_1/(R_e + r_e)` the ratio of response for a normal-mode signal to the response for a common-mode signal of the same amplitude.
        r_e -- Transresistance `r_e = V_T / I_e = ((kT) / q) / I_e = (0.0253 V) / I_e`
        """
        self.load(self.V)
        self.I_quiescent = self.I_load / 100

    def circuit(self):
        R = Resistor()

        self.R_c = self.V / 2 / self.I_quiescent
        self.R_e = self.R_load
        self.R_out = (0 @ u_V - self.V_inv) / (self.I_quiescent * 2)
        self.r_e = 0.026 @ u_V / self.I_quiescent
        self.G_diff = u(self.R_c / (2 * (self.r_e + self.R_e)))
        self.G_cm = u(-1 * self.R_c / (2 * self.R_out + self.R_e + self.r_e))
        self.CMMR = u(self.R_out / (self.R_e + self.r_e))

        amplifier = Bipolar(
            type='npn',
            common='emitter',
            follow='collector'
        )

        # First amplifier INVERTING
        left = amplifier(
            collector=R(self.R_c),
            emitter = R(self.R_e) # Emitter resistore conected to bipolar
        )
        right = amplifier(
            collector=R(self.R_c),
            emitter = R(self.R_e)
        )
        power = self.v_ref & left.v_ref & right.v_ref
        left_input = self.input & left & self.output_n
        right_input = self.input_n & right & self.output

        sink = left.gnd & right.gnd & R(self.R_out) & self.v_inv

