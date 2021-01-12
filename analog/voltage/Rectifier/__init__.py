from bem.abstract import Electrical

from PySpice.Unit import u_ms, u_Ohm, u_A, u_V, u_Hz, u_W


class Base(Electrical(port='two')):
    """# Diode Bridge

    A diode bridge is an arrangement of four (or more) diodes in a bridge circuit
    configuration that provides the same polarity of output for either polarity of input.

    ```
    vs = VS(flow='SINEV')(V=10, frequency=60, wire_gnd=False)

    load = Resistor()(1000)
    rectifier = Example()

    vs.output & rectifier.input
    vs.gnd & rectifier.input_n

    rectifier.output & load & rectifier.output_n
    rectifier.gnd & gnd

    # vs.gnd for simulation

    watch = rectifier
    ```

    * Paul Horowitz and Winfield Hill. "1.6.2 Rectification" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 31-32
    """

    def willMount(self):
        """
            V_ripple -- Periodic variations in voltage about the steady value
            frequency -- Input signal frequency
        """
        self.load(self.V)

    def circuit(self, **kwargs):
        self.create_bridge()


    def create_bridge(self):
        pass
