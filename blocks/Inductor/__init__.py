from bem import Block, Build
from skidl import Part, TEMPLATE
from PySpice.Unit import u_H

class Base(Block):
    increase = False
    value = 0 @ u_H

    def __init__(self, value, ref=None):
        if type(value) in [float, int]:
            value = float(value) @ u_H

        self.value = value.canonise()
        self.ref = ref
        self.circuit(value=value)

    @property
    def spice_part(self):
        return Build('L').spice

    @property
    def part(self):
        if self.DEBUG:
            return

        part = Part('Device', 'L', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('p', 1)
        part.set_pin_alias('n', 2)
        
        return part
