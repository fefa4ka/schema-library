from bem.abstract import Electrical, Network
from bem.basic import Resistor, Capacitor
from bem.basic.transistor import Bipolar
from bem.analog.voltage import Divider
from math import pi
from bem import Net, u, u_F, u_Ohm, u_V, u_Hz, u_A

class Modificator(Electrical()):
    """**Common-Emitter Amplifier**

    The circuit shown here is known as a common-emitter amplifier. Unlike the common-collector amplifier, the common-emitter amplifier provides voltage gain. This amplifier makes use of the common-emitter arrangement and is modified to allow for ac coupling.

    * Paul Scherz. "4.3.2 Bipolar Transistors" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 87


    """

    def willMount(self, f_3db=1000000 @ u_Hz):
        """
            f_3db -- Frequencies of interest are passed by the highpass filter
            C_in -- Blocking capacitor is chosen so that all frequencies of interest are passed by the highpass filter `C_(i\\n) >= 1 / (2 pi f_(3db) (R_s∥R_g))`
            I_quiescent --  That current puts the collector at `V_(ref)`
        """
        self.I_quiescent = self.I_load

    def circuit(self):
        amplifier = Bipolar(type='npn', emitter='amplifier')()
        self.v_ref & amplifier.v_ref
        self.gnd & amplifier.gnd

        self.C_in = (1 / (2 * pi * self.f_3db * amplifier.R_in_base_ac)) @ u_F
        self.C_out = (1 / (2 * pi * self.f_3db * (amplifier.r_e + amplifier.R_3))) @ u_F

        self.input & amplifier & self.output

        signal = Net('VoltageGainAcInput')
        ac_coupling = signal & Capacitor()(self.C_in) & self.input
        ac_out = amplifier.emitter & Resistor()(amplifier.R_3) & Capacitor()(self.C_in) & self.gnd

        self.input = signal


