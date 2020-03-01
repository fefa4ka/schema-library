from bem.abstract import Electrical

class Base(Electrical()):
    pins = {
        'v_ref': True,
        'gnd': True
    }

    def circuit(self):
        pass
