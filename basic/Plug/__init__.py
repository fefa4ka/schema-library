from bem.abstract import Physical
import inspect

class Base(Physical()):
    @classmethod
    def pins(self):
        pins = {
            'v_ref': True,
            'gnd': True
        }

        for interface in self.mods.get('interface', []):
            for pin in getattr(self, interface.upper()):
                pins[pin] = True

        return pins

    def circuit(self):
        element = self.part()

        self.element = element
