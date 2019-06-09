from .. import Base
from bem import Net, u_kOhm, u_nF, u_Ohm
from bem.basic import Switch, Resistor, Capacitor, Diode
from bem.abstract import Network

class Modificator(Base):
    def circuit(self):
        super().circuit()
        
        """
        The reset line has an internal pull-up resistor. If the environment is noisy, it can be insufficient and reset
        may occur sporadically. Refer to the device datasheet for the value of the pull-up resistor that must be
        used for specific devices.
        """
        pull_up = self['RESET'] & Resistor()(4.7 @ u_kOhm) & self.v_ref

        """
        If an external switch is connected to the RESET pin, it is important to add a series resistance. Whenever
        the switch is pressed, it will short the capacitor and the current (I) through the switch can have high peak
        values. This causes the switch to bounce and generate steep spikes in 2ms - 10ms (t) periods until the
        capacitor is discharged. The PCB tracks and the switch metal introduces a small inductance (L) and the
        high current through these tracks can generate high voltages up to VL = L * dI/dt.

        This spike voltage VL is most likely outside the specification of the RESET pin. By adding a series resistor
        between the switch and the capacitor, the peak currents generated will be significantly low and it will not
        be large enough to generate high voltages at the RESET pin. An example connection is shown in the
        following diagram.
        """
        switch = self['RESET'] & Resistor()(330 @ u_Ohm) & Switch(input='physical')() & self.gnd

        """
        To protect the RESET line from further noise, connect a capacitor from the RESET pin to ground. This is
        not directly required since the AVR internally have a low-pass filter to eliminate spikes and noise that
        could cause reset. Using an extra capacitor is an additional protection. However, such extra capacitor
        cannot be used when DebugWIRE or PDI is used.
        """
        noise_protect = self['RESET'] & Capacitor()(100 @ u_nF) & self.gnd

        """
        ESD protection diode is not provided internally from RESET to VCC in order to allow HVPP. If HVPP is not
        used, it is recommended to add an ESD protection diode externally from RESET to VCC. Alternatively, a
        Zener diode can be used to limit the RESET voltage relative to GND. A Zener diode is highly
        recommended in noisy environments. The components should be located physically close to the RESET
        pin of the AVR.Recommended circuit of a RESET line is shown in the following circuit diagram.
        """
        esd_protection = self['RESET'] & Diode()()['A, K'] & self.v_ref