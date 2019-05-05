from blocks.Abstract.Combination import Base as Block
from bem import Build
from skidl import Part, TEMPLATE
from PySpice.Unit import u_H

class Base(Block):
    """**Inductors**
    
    If you understand capacitors, you shouldn’t have great trouble with inductors. They’re closely related to capacitors: the rate of current change in an inductor is proportional to the voltage applied across it (for a capacitor it’s the other way around – the rate of voltage change is proportional to the current through it). 
    
    The defining equation for an inductor is:
    `V = L * (dI) / (dT)`

    Where L is called the inductance and is measured in henrys (or mH, μH, nH, etc.). Putting a constant voltage across an inductor causes the current to rise as a ramp (compare with a capacitor, in which a constant current causes the voltage to rise as a ramp); 
    
    1 V across 1 H produces a current that increases at 1 amp per second.

    **The energy** invested in ramping up the current in an inductor is stored internally, here in the form of magnetic fields. And the analogous formula is: `U_L = (L * I^2) / 2`

    A semi-empirical formula for the approximate inductance `L` of a coil of diameter `d` and length `l`, in which the `n^2` dependence is on display: `L ≈ K * (d^2 * n^2) / (18d + 40l) μH`

    * Paul Horowitz and Winfield Hill. "1.5.1 Inductors" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 28
    """

    increase = False
    value = 10 @ u_H 

    def willMount(self, value):
        """
            value -- L is called the inductance and is measured in henrys (or mH, μH, nH, etc.).
        """
        
        if type(value) in [float, int]:
            value = float(value) @ u_H
        
        self.value = self.value_closest(value) if not self.SIMULATION else value

    def part_spice(self, *args, **kwargs):
        return Build('L').spice(*args, **kwargs)

    def part_template(self):
        part = Part('Device', 'L', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('+', 1)
        part.set_pin_alias('-', 2)
        
        return part

    def circuit(self):
        super().circuit(value=self.value)