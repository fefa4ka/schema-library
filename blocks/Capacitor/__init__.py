from bem import Block
from skidl import Part, TEMPLATE


class Base(Block):
    increase = False
    
    def parallel_sum(self, values):
        return sum(values) @ u_Ohm

    def series_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    @property
    def spice_part(self):
        from skidl.pyspice import C

        return C

    @property
    def part(self):
        part = Part('Device', 'C', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('+', 1)
        part.set_pin_alias('-', 2)
        
        return part
