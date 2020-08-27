from bem.abstract import Electrical, Network

from PySpice.Unit import u_ms, u_Ohm, u_A, u_V, u_Hz, u_W


class Base(Network(port='two'), Electrical()):
    """# Diode Bridge

    A diode bridge is an arrangement of four (or more) diodes in a bridge circuit
    configuration that provides the same polarity of output for either polarity of input.

    ```
    vs = VS(flow='SINEV')(V=220, frequency=60)
    load = Resistor()(1000)
    rectifier = Example()

    vs & rectifier
    vs.gnd & rectifier.input_n

    rectifier.output & load & rectifier.output_n

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

    def __series__(self, instance):
        if self.output and instance.input:
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            self.output += instance.input

        if self.output_n and instance.input_n:
            self.output_n += instance.input_n

        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref

    def circuit(self, **kwargs):
        self.create_bridge()

    def create_bridge(self):
        pass
