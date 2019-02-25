from blocks.Abstract.Combination import Base as Block
from bem import Build
from skidl import Part, TEMPLATE
from PySpice.Unit import u_F
import numpy as np

class Base(Block):
    increase = False
    value = 1 @ u_F

    def __init__(self, value, ref=''):
        if type(value) in [float, int]:
            value = float(value) @ u_F

        self.value = self.value_closest(value) if not self.DEBUG else value
        
        self.ref = ref
        
        self.circuit(value=self.value)

    def parallel_sum(self, values):
        return sum(values) @ u_Ohm

    def series_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    @property
    def spice_part(self):
        return Build('C').spice

    @property
    def part(self):
        if self.DEBUG:
            return

        part = Part('Device', 'C', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('+', 1)
        part.set_pin_alias('-', 2)
        
        return part
