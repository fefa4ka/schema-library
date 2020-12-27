from bem.abstract import Electrical, Network
from bem.analog.voltage import Rectifier, Regulator
from bem.basic import Transformer

from bem import u_V, u_Hz

class Base(Network(port=['two']), Electrical()):
    """# Power Supply

    ```
    vs = VS(flow='SINEV')(V=220, frequency=60, wire_gnd=False)

    load = Resistor()(1000)

    power_supply = Example()

    vs.output & power_supply
    vs.gnd & power_supply.input_n
    power_supply.gnd & gnd

    power_supply.output & load & gnd

    watch = power_supply
    ```

    * Paul Horowitz and Winfield Hill. "1.6.2 Rectification" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 31-32
    """
    def willMount(self,
                  V=220 @ u_V,
                  V_out=3.3 @ u_V,
                  Frequency=60 @ u_Hz):
        """
        V_stiff -- Integrated NPN regulator needs at least 2 * V_be of "dropout voltage"
        """
        self.V_stiff = self.V_out * 2

    def circuit(self):
        transformer = Transformer()(V_out=self.V_stiff)

        # TODO: Fuses before
        # self.input & switch & fuse
        rectifier = Rectifier(wave='full', rectifier='full')(
            V = self.V_stiff, 
            V_ripple = self.V_stiff * 0.01
        )

        # TODO: Filter
        # Regulator
        regulator = Regulator(via='ic', stability='bypass')(
            V = self.V_stiff,
            V_out = self.V_out
        )

        self.input & transformer.input
        self.input_n & transformer.input_n & self.gnd
        transformer.gnd & self.gnd

        transformer & rectifier & regulator & self.output

