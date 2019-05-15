from bem.abstract import Electrical

class Base(Electrical()):
    mods = {
        'split': ['unity']
    }

    pins = {
        'v_ref': True,
        'input': ('Some', ['output']),
        'output_n': True,
        'gnd': True
    }
    
    def circuit(self):
        pass 