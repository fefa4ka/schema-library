from bem.abstract import Electrical

class Base(Electrical()):
    pins = {
        'v_ref': True,
        'input': ('Body', ['output']),
        'gnd': True
    }

    def willMount(self):
        self.output = self.input

    def circuit(self):
        pass

