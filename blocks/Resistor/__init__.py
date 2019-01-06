
from blocks.Combination import Base as Block
from skidl import Part, Net, subcircuit, TEMPLATE
from PySpice.Unit import u_Ohm, u_V
import numpy as np
import logging

class Base(Block):
    increase = True

    def series_sum(self, values):
        return sum(values) @ u_Ohm

    def parallel_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    def power(self, voltage):
        return voltage * voltage / self.value
        
    @property
    def part(self):
        part = Part('Device', 'R', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('p', 1)
        part.set_pin_alias('n', 2)

        return part


    @subcircuit
    def create_circuit(self, value):
        R_model = None
        if self.DEBUG:
            from skidl.pyspice import R

            R_model = R
        else:
            R_model = self.part
        
        instance = self.clone
        instance.value = value
    
        values = self.values_optimal(instance.value, error=5)
        resistors = []
        rin = Net()
        rout = Net()
        
        self.log(f'{value} implemented by {len(values)} resistors: ' + ', '.join([str(value) + " Ω" for value in values]))

        for index, value in enumerate(values):
            if type(value) == list:
                parallel_in = Net()
                parallel_out = Net()
                
                for resistance in value:
                    r = R_model(value=resistance)

                    r[1] += parallel_in
                    r[2] += parallel_out
                
                if index:
                    previous_r = resistors[-1]
                    previous_r[2] += parallel_in[1]

                resistors.append((None, parallel_in, parallel_out))

            else:
                r = R_model(value = value)

                if index:
                    previous_r = resistors[-1]
                    previous_r[2] += r[1]
                
                resistors.append(r)
        
        rin += resistors[0][1]
        rout += resistors[-1][2]
        
        instance.input = rin
        instance.output = rout
        
        return instance
