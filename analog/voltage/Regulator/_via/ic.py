from .. import Base
from bem.abstract import Physical

class Modificator(Base, Physical()):
    """
    * https://webench.ti.com/power-designer/switching-regulator/customize/2?AppType=none&O1I=0.5&O1V=12&VinMax=15&VinMin=13.5&action=simulate&base_pn=LM1117-ADJ&flavor=ADJ&lang_chosen=en_US&op_TA=30&optfactor=3&origin=pf_panel
    """
    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'gnd': True
    }

    def circuit(self):
        self.element = self.part()
        
        # In Spice models pins defined as below
        pins = {
            'input': ['VI', 'VIN', 'IN'],
            'output': ['VO', 'VOUT', 'OUT'],
            'gnd': ['GND', 'ADJ']
        }

        for pin in pins.keys():
            for part_pin in pins[pin]:
                if self.element[part_pin]:
                    print(self.element[part_pin], getattr(self, pin))
                    self.element[part_pin] += getattr(self, pin)
                    break

        self.v_ref = self.input


