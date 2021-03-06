from bem.abstract import Electrical
from bem.basic.transistor import Bipolar


class Base(Electrical()):
    """
        ## PushPull power booster
        Bipolar follower booster has the usual problem that the follower output can only source current. As with transistor circuits, the remedy is a push–pull booster.

        * Paul Horowitz and Winfield Hill. "4.3.1 Linear circuits" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p.435
    """
    pins = {
        'v_ref': True,
        'input': True,
        'output': True,
        'v_inv': True,
        'gnd': True
    }

    def circuit(self):
        up = Bipolar(type='npn')()
        down = Bipolar(type='pnp')()

        self.wire_input(up, down)
        self.output & up.emitter & down.emitter

        self.v_ref & up.v_ref
        self.v_inv & down.collector

    def wire_input(self, up, down):
        self.input += up.base, down.base
