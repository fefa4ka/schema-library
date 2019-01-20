
from blocks.Combination import Base as Block
from skidl import Part, Net, subcircuit, TEMPLATE
from PySpice.Unit import u_Ohm, u_V
import numpy as np
import logging

class Base(Block):
    """Resistor
    
    Generic resistance. 
    Resistance implemented by combination of series or parallel connected resistors from available values in stock. 
    """

    increase = True
    value = 0 @ u_Ohm

    def __init__(self, value):
        self.value = value.canonise()
        
        self.circuit()

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
    def circuit(self):
        R_model = None
        if self.DEBUG:
            from skidl.pyspice import R

            R_model = R
        else:
            R_model = self.part
    
        values = self.values_optimal(self.value, error=5)
        resistors = []
        rin = Net()
        rout = Net()
        
        self.log(f'{self.value} implemented by {len(values)} resistors: ' + ', '.join([str(value) + " Ω" for value in values]))

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
        
        self.input = rin
        self.output = rout