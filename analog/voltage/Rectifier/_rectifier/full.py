from .. import Base
from bem.basic import Capacitor
from bem import Net
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Base):
    """
        **Power-supply filtering**

        The preceding rectified waveforms aren’t good for much as
        they stand. They’re “dc” only in the sense that they don’t
        change polarity. But they still have a lot of “ripple”
        (periodic variations in voltage about the steady value) that has
        to be smoothed out in order to generate genuine dc. This
        we do by attaching a relatively large value capacitor;
        it charges up to the peak output voltage during
        the diode conduction, and its stored charge (`Q = CV`)
        provides the output current in between charging cycles. Note
        that the diodes prevent the capacitor from discharging back
        through the ac source.

        If you assume that the load current stays constant (it will, for small ripple), you have
        `ΔV = I_(load)/(fC_(rippl\e))`

        * Paul Horowitz and Winfield Hill. "1.6.3 Power-supply filtering" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 32-33
    """

    def willMount(self, V_ripple=1 @ u_V, frequency=120 @ u_Hz):
        """
            V_ripple -- Periodic variations in voltage about the steady value
            frequency -- Input signal frequency
            C_ripple -- A relatively large value capacitor; it charges up to the peak output voltage during the diode conduction.  The capacitor value is chosen so that `R_(load)C_(rippl\e) ≫ 1/f`
        """
        pass

    def circuit(self):
        super().circuit()

        is_full_wave = 'full' in self.mods['wave']
        bridge_output = self.output
        self.output = Net('BridgeOutput')

        self.C_ripple = (self.I_load / (self.frequency * self.V_ripple * (2 if is_full_wave else 1))) @ u_F
        C_ripple = Capacitor()(value=self.C_ripple, ref='C_ripple', **self.load_args)

        circuit = bridge_output & self.output & C_ripple & self.output_n
