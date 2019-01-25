from bem import Block, Build
from skidl import Part, TEMPLATE


class Base(Block):
    @property
    def spice_part(self):
        return Build('D').spice

    @property
    def part(self):
        if self.DEBUG:
            return

        part = Part('Device', 'D', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('A', 1)
        part.set_pin_alias('K', 2)
        
        return part
