from .. import Base
from bem.basic import Resistor
from bem.analog.voltage import Divider
from math import pi
from bem import Net, u, u_F, u_Ohm, u_V, u_Hz, u_A

R = Resistor()

class Modificator(Base):
    """**Common-Emitter Amplifier**

    The circuit shown here is known as a common-emitter amplifier. Unlike the common-collector amplifier, the common-emitter amplifier provides voltage gain. This amplifier makes use of the common-emitter arrangement and is modified to allow for ac coupling.

    * Paul Scherz. "4.3.2 Bipolar Transistors" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 87


    """

    def willMount(self):
        """
            I_quiescent --  That current puts the collector at `V_(ref)`

            V_je -- Base-emitter built-in potential
            V_e -- `V_e = 1V` selected for temperature stability and maximum voltage swing
            V_c -- `V_c = V_(ref) / 2`
            R_c -- `R_c = (V_(ref) - V_c) / I_(quiescent)`
            R_in -- `1/R_(i\\n) = 1/R_s + 1/R_g + 1 / R_(i\\n(base))`
            R_e -- `R_e = V_e / I_(load)`

            R_in_base_dc -- `R_(i\\n(base),dc) = beta * R_e`
            R_in_base_ac -- `R_(i\\n(base),ac) = beta * (r_e + R_(load))`

            G_v -- Amplifier gain `G_v = v_(out) / v_(i\\n) = - g_m * R_c = -R_c/R_e`
            g_m -- The inverse of resistance is called conductance. An amplifier whose gain has units of conductance is called a transconductance amplifier. `g_m = i_(out)/v_(i\\n) = - G_v / R_c `
            r_e -- Transresistance `r_e = V_T / I_e = ((kT) / q) / I_e = (0.0253 V) / I_e`

        """
        self.props['follow'] = 'collector'
        self.props['common'] = 'emitter'

        self.I_quiescent = self.I_load

        self.V_c = self.V / 2
        self.R_c = (self.V - self.V_c) / self.I_quiescent

        self.V_e = 1.0 @ u_V  # For temperature stability
        self.R_e = self.V_e / self.I_quiescent

        self.r_e = 0.026 @ u_V / self.I_quiescent

        self.G_v = -1 * u(self.R_c / (self.R_e + self.r_e))
        self.R_3 = (-1 * self.R_c - self.r_e * self.G_v) / self.G_v

        self.g_m = self.G_v / self.R_c * -1

        self.R_in_base_dc = self.Beta * self.R_e
        self.R_in_base_ac = self.Beta * (self.r_e + self.R_3)

        self.Power = (self.V_c - self.V_e) * self.I_quiescent
        self.consumption(self.V_c)

    def circuit(self):
        self.collector = R(self.R_c)
        self.emitter = R(self.R_e)

        super().circuit()

        stiff_voltage = Divider(type='resistive')(
            V = self.V,
            V_out = self.V_e + self.V_je,
            Load = self.Beta * self.R_e
        )
        self.v_ref & stiff_voltage & self
        stiff_voltage.gnd & self.gnd

        self.R_in = R.parallel_sum(R, [self.R_in_base_ac, stiff_voltage.R_in, stiff_voltage.R_out])
