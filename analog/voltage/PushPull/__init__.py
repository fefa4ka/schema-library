from bem.abstract import Electrical
from bem.basic.transistor import Bipolar


class Base(Electrical()):
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
        up.emitter & down.emitter & self.output

        self.v_ref & up.v_ref
        self.v_inv & down.collector

    def wire_input(self, up, down):
        self.input += up.base, down.base
