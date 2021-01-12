from bem import u_A, u_V

class Modificator:
    """
    ## Zener Diode
    Zeners are used to create a constant voltage inside a circuit somewhere, simply done by providing
    them with a (roughly constant) current derived from a higher voltage within the circuit

    A zener diode acts like a two-way gate to current flow. In the forward direction, it’s easy to push open;
    only about 0.6 V—just like a standard diode. In the reverse direction, it’s harder to push open; it requires
    a voltage equal to the zener’s breakdown voltage VZ. This breakdown voltage can be anywhere
    between 1.8 and 200 V, depending on the model (1N5225B = 3.0 V, 1N4733A = 5.1 V, 1N4739A = 9.1 V, etc.).
    Power ratings vary from around 0.25 to 50 W.

    For example, the zener diode will convert an applied current in the range shown to a corresponding (but fractionally narrower) range of voltages


   ```
    vs = VS(flow='V')(V=slice(-10, 10, .1))
    load = Resistor()(1000)
    zener = Example()
    vs & zener & load & vs

    watch = zener
    ```

    * Paul Horowitz and Winfield Hill. "1.2.6 Small-signal resistance" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 12-13
    * Paul Scherz. "4.2.6 Zener Diodes" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    * https://github.com/peteut/spice-models/blob/master/diodes/diodes/diodes_zener-diodes.txt
    * http://espice.ugr.es/espice/src/modelos_subckt/spice_complete/cadlab.lib
    * https://www.electronics-notes.com/articles/electronic_components/diode/zener-diode-datasheet-specifications-parameters.php

    """

    def circuit(self):
        self.I_max = float(self['P']) / float(self['BV']) @ u_A

        super().circuit()
