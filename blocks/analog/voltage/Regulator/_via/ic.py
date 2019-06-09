from .. import Base
from skidl import Part, Net, TEMPLATE
from bem import Build
from bem.abstract import Physical
from bem.basic import Resistor
from bem.basic.transistor import Bipolar

from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Physical(), Base):
    """
    """

    def part_spice(self, *args, **kwargs):
        part = Build(self.selected_part.scheme or self.model + ':' + self.model).spice
        part.set_pin_alias('VI', '3')
        part.set_pin_alias('VO', '1')
        part.set_pin_alias('GND', '2')

        return part(*args, **kwargs)

    def part_template(self):
        part = Part('Regulator_Linear', self.selected_part.scheme or self.model, footprint=self.footprint, dest=TEMPLATE)
        
        return part

    def circuit(self):
        self.element = self.part()

        self.input += self.element['VI']
        self.output += self.element['VO']
        self.gnd += self.element['GND']
        
        self.output += self.v_ref
        
   
        

