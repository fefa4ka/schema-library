from bem.abstract import Physical
import inspect

class Base(Physical()):
    @classmethod
    def pins(cls):
        pins = {
            'v_ref': True,
            'gnd': True
        }

        for interface in cls.mods.get('interface', []):
            for pin in getattr(cls, interface.upper()):
                pins[pin] = True

        return pins

    def circuit(self):
        element = self.part()

        self.element = element
