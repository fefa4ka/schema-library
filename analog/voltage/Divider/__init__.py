from bem import u_Ohm, u_V, u_A
from bem.abstract import Electrical


class Base(Electrical()):
    """# Voltage Divider
    Voltage dividers are often used in circuits to gener- ate a particular voltage from a larger fixed (or varying) voltage.

    Voltage divider from `V_(\i\\n)` to `V_(out)` could be implemented in different ways and provide enought current to `Load`.

    This isn’t as crazy as it sounds; it is possible to make devices with negative “incremental” resistances (e.g., the component known as a tunnel diode) or even true negative resistances (e.g., the negative-impedance converter). 

    * Paul Horowitz and Winfield Hill. "1.2.3 Voltage Dividers" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 7-8
    """

    # Props
    def willMount(self, V=5 @ u_V, V_out=3 @ u_V, Load=0.01 @ u_A):
        """
           V_out -- Note that the output voltage is always less than (or equal to) the input voltage; that’s why it’s called a divider.
        """
        self.load(self.V_out)
