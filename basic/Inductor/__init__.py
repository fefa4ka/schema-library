from bem import Build
from bem.abstract import Combination
from skidl import Part, TEMPLATE
from PySpice.Unit import u_H

class Base(Combination()):
    """# Inductors

    If you understand capacitors, you shouldn’t have great trouble with inductors. They’re closely related to capacitors: the rate of current change in an inductor is proportional to the voltage applied across it (for a capacitor it’s the other way around – the rate of voltage change is proportional to the current through it). 

    The defining equation for an inductor is:
    `V = L * (dI) / (dT)`

    ```
    vs = VS(flow='SINEV')(V=5, frequency=[1e3, 1e6])
    load = Resistor()(1000)
    inductor = Example()
    vs & inductor & load & vs

    watch = inductor
    ```

    Where `L` is called the inductance and is measured in henrys (or mH, μH, nH, etc.). Putting a constant voltage across an inductor causes the current to rise as a ramp (compare with a capacitor, in which a constant current causes the voltage to rise as a ramp); 

    1 V across 1 H produces a current that increases at 1 amp per second.


    **The energy** invested in ramping up the current in an inductor is stored internally, here in the form of magnetic fields. And the analogous formula is: `U_L = (L * I^2) / 2`

    A semi-empirical formula for the approximate inductance `L` of a coil of diameter `d` and length `l`, in which the `n^2` dependence is on display: `L ≈ K * (d^2 * n^2) / (18d + 40l) μH`

    * Paul Horowitz and Winfield Hill. "1.5.1 Inductors" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 28
    """

    increase = False

    def willMount(self, value = 0.001 @ u_H):
        """
            value -- L is called the inductance and is measured in henrys (or mH, μH, nH, etc.).
        """
        pass

    def part_spice(self, *args, **kwargs):
        return Build('L').spice(*args, **kwargs)
