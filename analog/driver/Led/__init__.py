from bem.abstract import Electrical, Network


class Base(Electrical()):
    diodes = []

    pins = {
        'v_ref': ('Supply', ['input']),
        'gnd': ('Gnd', ['output'])
    }

    def willMount(self, diodes):
        if type(diodes) != list:
            self.diodes = [diodes]
