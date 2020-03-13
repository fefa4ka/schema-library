from .. import Base
from bem.analog.voltage import Divider
from bem.basic import Resistor

from bem import Net, u, u_Ohm, u_V, u_A

class Modificator(Base):
    """**Emitter-Follower** Common-Collector Amplifier

    The circuit shown here is called a common-collector amplifier, which has current gain but no voltage gain. It makes use of the emitter-follower arrangement but is modified to avoid clipping during negative input swings. The voltage divider (`R_s` and `R_g`) is used to give the input signal (after passing through the capacitor) a positive dc level or operating point (known as the quiescent point). Both the input and output capacitors are included so that an ac input-output signal can be added without disturbing the dc operating point. The capacitors, as you will see, also act as filtering elements.”

    * Paul Scherz. “Practical Electronics for Inventors, Fourth Edition
    """

    V = 10 @ u_V

    I_in = 0 @ u_A
    R_e = 0 @ u_Ohm
    Beta = 100

    def willMount(self):
        """
        R_in -- `1/R_(i\\n) = 1/R_s + 1/R_g + 1 / R_(i\\n(base))`
        R_e -- `R_e = V_e / I_(load)`
        V_je -- Base-emitter built-in potential
        V_e -- `V_e = V_(ref) / 2`
        V_b -- `V_b = V_e + V_(je)`
        I_in -- `I_(i\\n) = I_(load) / beta`
        R_in_base_dc -- `R_(i\\n(base),dc) = beta * R_e`
        R_in_base_ac -- `R_(i\\n(base),ac) = beta * (R_e * R_(load)) / (R_e + R_(load))`
        """

        self.load(self.V)

        self.props['common'] = 'emitter'
        self.props['follow'] = 'emitter'

        self.V_e = self.V / 2
        self.R_e = self.V_e / self.I_load

        self.R_in_base_dc = self.Beta * self.R_e
        self.R_in_base_ac = self.Beta * ((self.R_e * self.R_load) / (self.R_e + self.R_load))

        self.I_in = self.I_load / self.Beta

    def circuit(self):
        R = Resistor()
        self.emitter = R(self.R_e)

        super().circuit()


        stiff_voltage = Divider(type='resistive')(
            V = self.V,
            V_out = self.V_e + self.V_je,
            Load = self.I_in
        )
        stiff_voltage.gnd & self.gnd

        self.v_ref & stiff_voltage & self.input

        self.R_in = R.parallel_sum(R, [self.R_in_base_dc, stiff_voltage.R_in, stiff_voltage.R_out]) 


