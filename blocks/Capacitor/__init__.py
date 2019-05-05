from blocks.Abstract.Combination import Base as Block
from bem import Build
from skidl import Part, TEMPLATE
from PySpice.Unit import u_F, u_V, u_C, u_J
import numpy as np

class Base(Block):
    """
        A capacitor (the old-fashioned name was condenser) is a device that has two wires sticking out of it and has the property
       `Q = CV` (1)

        A capacitor of `C` farads with `V` volts across its terminals has `Q` coulombs of stored charge on one plate and `−Q` on the other. 
        
        Taking the derivative of the defining equation 1, you get
        `I = C (dV)/(dt)`

        So a capacitor is more complicated than a resistor: the current is not simply proportional to the voltage, but rather to the rate of change of voltage. If you change the voltage across a farad by 1 volt per second, you are supplying an amp. Conversely, if you supply an amp, its voltage changes by 1 volt per second. A farad is an enormous capacitance, and you usually deal in microfarads (μF), nanofarads (nF), or picofarads (pF).

        When you charge up a capacitor, you’re supplying energy. The capacitor doesn’t get hot; instead, it stores the energy in its internal electric fields.

        * Paul Horowitz and Winfield Hill. "1.4.1 Capacitors" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 51-52
    """
    
    increase = False
    value = 1 @ u_F
    Q = 0 @ u_C
    U_C = 0 @ u_J

    def willMount(self, value):
        """
            value -- The capacitance is proportional to the area and inversely proportional to the spacing. For the simple parallel-plate capacitor, with separation `d` and plate area `A` (and with the spacing `d` much less than the dimensions of the plates), the capacitance `C` is given by `C = 8.85 xx 10^-14 (εA)/d F` where `ε` is the [dielectric constant](https://en.wikipedia.org/wiki/Relative_permittivity) of the insulator, and the dimensions are measured in centimeters.
            Q -- A capacitor of `C` farads with `V` volts across its terminals has `Q` coulombs of stored charge on one plate and `−Q` on the other. 
            U_C -- The capacitor stores the energy in its internal electric fields. The amount of stored energy in a charged capacitor is just `U_C = (CV^2)/2`
        """
        
        if type(value) in [float, int]:
            value = float(value) @ u_F

        self.value = self.value_closest(value) if not self.SIMULATION else value

        self.consumption(0)

        self.Q = self.value * self.V
        self.U_C = self.value * self.V * self.V / 2

    def parallel_sum(self, values):
        return sum(values) @ u_Ohm

    def series_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    def part_spice(self, *args, **kwargs):
        return Build('C').spice(*args, **kwargs)

    def part_template(self):
        part = Part('Device', 'C', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('+', 1)
        part.set_pin_alias('-', 2)
        
        return part

    def circuit(self):
        super().circuit(value=self.value)