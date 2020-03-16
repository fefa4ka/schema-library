from bem.abstract import Electrical

class Base(Electrical()):
    pins = {
        'v_ref': True,
        'input': True,
        'output': True,
        'gnd': True
    }

    def circuit(self):
        self.input & self.output
