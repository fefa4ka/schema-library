from .. import Base
from bem.basic import Resistor, Diode
from bem.basic.transistor import Bipolar
from bem import u

from PySpice.Unit import u_Ohm, u_V, u_A, u_F, u_W

class Modificator(Base):
    """## Zener Voltage Regulator

    The simplest regulated supply of voltage is simply a zener.

    These circuits act as voltage regulators, preventing any supply voltage or load current variations
    from pulling down the voltage supplied to the load.

    Note that zener regulators are somewhat temperature dependent and aren’t the best choice for critical applications

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83
    * Paul Scherz. "4.2.6 Zener Diodes" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016

    """

    def circuit(self, **kwargs):
        R_source = (self.V - self.V_out) / self.I_load / 10

        P_zener = ((self.V - self.V_out) / R_source - self.I_load) * self.V_out

        # The zener must be able to dissipate `P_(zen\er) =  ((V - V_(out))/R_(source) - I_(load)) * V_(out)`
        regulator = Diode(
            type='zener',
            BV=self.V_out,
            P=P_zener,
            upper_limit=self.props.get('upper_limit', [])
        )()

        self.V_out = regulator['BV']

        if 'lowpass' not in self.mods.get('stability', []):
            # Some current must flow through the zener, so you choose `(V_(min) - V_(out))/R_(source) > I_(load)(max)`
            source = Resistor()(R_source)
            self.input & source & self.output

        self.output & regulator['K, A'] & self.gnd



