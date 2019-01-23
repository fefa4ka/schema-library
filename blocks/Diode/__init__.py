from bem import Block
from skidl import Part, TEMPLATE


class Base(Block):
    @property
    def spice_part(self):
        from skidl.pyspice import D

        return D

    @property
    def part(self):
        if self.DEBUG:
            return

        part = Part('Device', 'D', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('A', 1)
        part.set_pin_alias('K', 2)
        
        return part
