
from bem.abstract import Electrical, Network
from bem.analog.voltage import Divider
from bem.basic import Resistor
from bem.basic.transistor import Bipolar
from bem import u, u_ms, u_Ohm, u_A, u_V

from settings import params_tolerance
from random import randint

class Base(Electrical(), Network(port='two')):
    """**Transistor Current Source**

    Happily, it is possible to make a very good current source with a transistor. It works like this: applying `V_b` to the base, with `V_b>0.6 V`, ensures that the emitter is always conducting:

    `V_e = V_b − 0.6 V`
    so
    `I_e = V_e / R_e = (V_b − 0.6 V) / R_e`

    But, since `I_e ≈ I_(load)` for large beta,
    `I_(load) ≈ (V_b − 0.6 V) / R_e`

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 86

    """

    pins = {
        'v_ref': ('Vref', ['input', 'output']),
        'output_n': True,
        'gnd': True
    }

    def willMount(self, Load=0.001 @ u_A):
        """

        """
        self.load(self.V)

    def circuit(self, **kwargs):
        generator = Bipolar(type='npn', follow='emitter')()

        self.V_e = generator.V_je + randint(1, int(u(self.V) / 2)) @ u_V
        self.V_b = self.V_e + generator.V_je
        self.R_e = self.V_e / self.I_load

        generator.collector += self.output_n

        controller = Divider(type='resistive')(
            V = self.V,
            V_out = self.V_b,
            Load = self.I_load
        )

        controller.input += self.v_ref
        controller.gnd += self.gnd

        source = controller.output & generator & Resistor()(self.R_e) & self.gnd
