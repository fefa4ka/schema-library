from .. import Base
from skidl import Part, TEMPLATE

class Modificator(Base):
    def part_template(self):
        part = Part('Device', 'Crystal', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('+', 1)
        part.set_pin_alias('-', 2)
        
        return part