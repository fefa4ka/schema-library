from .. import Base
from bem.analog.voltage import Divider
from bem.analog import Filter
from bem import u_Hz
from bem.basic import Resistor

from bem import Net, u, u_Ohm, u_V, u_A

class Modificator(Base):
    """## Emitter-Follower Common-Collector Amplifier
    The circuit shown here is called a common-collector amplifier (emitter-follower), which has current gain but no voltage gain. 
    It is called that because the output terminal is the emitter, which follows the input (the base), less one diode drop. The output is a replica of the input, but `V_(je)` less positive.

    By returning the emitter resistor to a negative supply voltage, you can permit negative voltage swings as well.

    """

    V = 10 @ u_V

    I_in = 0 @ u_A
    R_e = 0 @ u_Ohm
    Beta = 100

    def willMount(self, Frequency=0 @ u_Hz):
        """
        R_in -- `1/R_(i\\n) = 1/R_s + 1/R_g + 1 / R_(i\\n(base))`
        V_je -- Base-emitter built-in potential
        V_e -- For the largest possible symmetrical swing without clipping `V_e = V_(ref) / 2`
        V_b -- `V_b = V_e + V_(je)`
        I_in -- `I_(i\\n) = I_(load) / beta`
        Z_in -- `Z_(i\\n) = 1/R_(i\\n) = 1/R_s + 1/R_g + 1 / R_(i\\n(base))`
        Z_out -- `Z_(out) = R_e||[(Z_(i\\n)||R_(i\\n)||R_(out)) / beta]`
        Z_in_base_dc -- `Z_(i\\n(base),dc) = beta * R_e`
        Z_in_base_ac -- `Z_(i\\n(base),ac) = beta * (R_e * R_(load)) / (R_e + R_(load))`
        """

        self.load(self.V)

        self.props['common'] = 'emitter'
        self.props['follow'] = 'emitter'

        self.V_e = self.V / 2

    def circuit(self):
        R = Resistor()
        # For a quescent current of `I_(load)`
        # `R_e = V_e / I_(load)`
        self.emitter = R(self.V_e / self.I_load)
        R_e = self.emitter.value

        super().circuit()

        self.I_in = self.I_load / self.Beta

        #  It is necessary to bias the follower (in fact, any transistor amplifier) so that collector current flows during the entire signal swing. In this case a voltage divider is the simplest way. (`R_(i\nput)` and `R_(output)` are chosen to put the base halfway between ground and `V` when there is no input signal, setting operating point (known as the quiescent point).
        stiff_voltage = Divider(type='resistive')(
            V = self.V,
            V_out = self.V_e + self.V_je,
            Load = self.I_in
        )
        stiff_voltage.gnd & self.gnd

        self.v_ref & stiff_voltage

        if self.Frequency:
            # The capacitor `C_(resonator)` forms a highpass filter with the impedance it sees as a load, namely the impedance looking into the base in parallel with the impedance looking into the base voltage divider. If we assume that the load this circuit will drive is large compared with the emitter resistor, then the impedance looking into the base is `βRE`.
            pre_filter = Filter(highpass='rc')(
                f_3dB_high = self.Frequency,
                R_shunt=stiff_voltage.R_out
            )

            ac_input = Net("AcCoupledInput")
            ac_input & pre_filter & stiff_voltage.output & self.input
            self.input = ac_input

            # The capacitor `C_(resonator)` forms a highpass filter in combination with the load impedance, which is unknown. However, it is safe to assume that the load impedance won’t be smaller than `R_e`.
            post_filter = Filter(highpass='rc')(
                f_3dB_high = self.Frequency,
                R_shunt=R_e
            )

            ac_output = Net("AcCoupledOutput")
            self.output & post_filter & ac_output
            self.output = ac_output


        self.Z_in_base_dc = self.Beta * R_e
        self.Z_in_base_ac = self.Beta * ((R_e * self.R_load) / (R_e + self.R_load))
        psum = lambda values: R.parallel_sum(R, values) @ u_Ohm
        self.Z_in = psum([self.Z_in_base_dc, stiff_voltage.R_in, stiff_voltage.R_out])
        self.Z_out = psum([R_e, psum([self.Z_in, stiff_voltage.R_in, stiff_voltage.R_out]) / self.Beta])
        self.Power = self.V_e * self.I_load

