from bem.abstract import Electrical, Network
from bem.basic import Resistor, Capacitor
from bem.basic.transistor import Bipolar
from bem.analog.voltage import Divider
from math import pi
from bem import Net, u, u_F, u_Ohm, u_V, u_Hz, u_A

class Base(Network(port='two'), Electrical()):
    """**Common-Emitter Amplifier**
    
    The circuit shown here is known as a common-emitter amplifier. Unlike the common-collector amplifier, the common-emitter amplifier provides voltage gain. This amplifier makes use of the common-emitter arrangement and is modified to allow for ac coupling.

    * Paul Scherz. "4.3.2 Bipolar Transistors" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 87
    

    """

    V_ref = 20 @ u_V
    V = 1.4 @ u_V
    f_3db = 1000000 @ u_Hz
    I_quiescent = 0.01 @ u_A

    G_v = -100
    C_in = 0 @ u_F
    R_c = 0 @ u_F
    R_e = 0 @ u_F
    
    def willMount(self, V_ref, f_3db, I_quiescent):
        """
            f_3db -- Frequencies of interest are passed by the highpass filter
            C_in -- Blocking capacitor is chosen so that all frequencies of interest are passed by the highpass filter `C_(i\\n) >= 1 / (2 pi f_(3db) (R_s∥R_g))`
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
        pass

    def circuit(self):
        self.input = self.output = Net('VoltageGainInput')
        self.v_ref = Net('Vref')
        self.gnd = Net()

        self.V_c = self.V_ref / 2
        self.R_c = (self.V_ref - self.V_c) / self.I_quiescent

        self.V_e = 1.0 @ u_V  # For temperature stability
        self.R_e = self.V_e / self.I_quiescent 
        
        R = Resistor()

        amplifier = Bipolar(
            common='emitter',
            follow='collector'
        )(
            collector = R(self.R_c, ref='R_c'),
            emitter = R(self.R_e, ref='R_e')
        )

        self.Beta = amplifier.selected_part.spice_params.get('BF', 100)
        self.V_je = (amplifier.selected_part.spice_params.get('VJE', None) or 0.6) @ u_V

        stiff_voltage = Divider(type='resistive')(
            V = self.V_ref,
            V_out = self.V_e + self.V_je,
            Load = self.Beta * self.R_e
        )

        self.r_e = 0.026 @ u_V / self.I_quiescent

        self.G_v = -1 * u(self.R_c / (self.R_e + self.r_e))
        self.R_3 = (-1 * self.R_c - self.r_e * self.G_v) / self.G_v

        self.g_m = self.G_v / self.R_c * -1

        self.R_in_base_dc = self.Beta * self.R_e
        
        self.R_in_base_ac = self.Beta * (self.r_e + self.R_3)
        self.R_in = R.parallel(R, [self.R_in_base_ac, stiff_voltage.R_in, stiff_voltage.R_out]).Z.evaluate() @ u_Ohm
      
        stiff_voltage.input += self.v_ref

        self.C_in = (1 / (2 * pi * self.f_3db * self.R_in)) @ u_F
        self.C_out = (1 / (2 * pi * self.f_3db * (self.r_e + self.R_3))) @ u_F
        
        amplified = Net('VoltageGainOutput')

        circuit = stiff_voltage & self & amplifier & amplified
        
        signal = Net('VoltageGainAcInput')
        ac_coupling = signal & Capacitor()(self.C_in) & self.input
        ac_out = amplifier.emitter & R(self.R_3, ref='R_ac') & Capacitor()(self.C_in) & self.gnd

        self.input = signal
        self.output = amplified

        self.Power = (self.V_c - self.V_e) * self.I_quiescent
        self.consumption(self.V_c)
