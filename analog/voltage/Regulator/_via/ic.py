from .. import Base
from bem.abstract import Physical

class Modificator(Base, Physical()):
    """
    """
    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'gnd': True
    }

    def circuit(self):
        self.element = self.part()

        pins = {
            'input': ['VI', 'VIN', 'IN'],
            'output': ['VO', 'VOUT', 'OUT'],
            'gnd': ['GND', 'ADJ']
        }

        for pin in pins.keys():
            for part_pin in pins[pin]:
                if self.element[part_pin]:
                    self.element[part_pin] += getattr(self, pin)
                    break

        self.v_ref = self.input


