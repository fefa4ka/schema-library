from bem.abstract import Electrical, Network


class Base(Electrical()):
    diodes = []

    pins = {
        'v_ref': ('Supply', ['input', 'output']),
        'gnd': True
    }

    def willMount(self, diodes):
        if type(diodes) != list:
            self.diodes = [diodes]
