
from blocks.Abstract.Combination import Base as Block
from skidl import Part, Net, subcircuit, TEMPLATE
from PySpice.Unit import u_Ohm, u_V, u_W, u_A
import numpy as np
from bem import Build
import logging

class Base(Block):
    """Resistor
    
    Generic resistance. 
    Resistance implemented by combination of series or parallel connected resistors from available values in stock. 
    """

    increase = True
    value = 1000 @ u_Ohm
    V_in = 10 @ u_V
    R_load = 1000 @ u_Ohm
    P = 0 @ u_W
    I = 0 @ u_A
    V_drop = 0 @ u_V

    ref = 'R'

    def __init__(self, value, V_in=None, R_load=None, ref=''):
        if type(value) in [str, int, float]:
            value = float(value) @ u_Ohm

        self.value = value
        
        if ref:
            self.ref = ref

        self.circuit()
        self.calculator(V_in, R_load)
    
    def calculator(self, V_in=None, R_load=None):
        # Power Dissipation
        total_value = self.value.value * self.value.scale

        V_in_value = self.V_in.scale * self.V_in.value
        self.P = self.power(V_in_value, total_value) @ u_W
        self.I = self.current(V_in_value, total_value) @ u_A
        I_total =self.current(V_in_value, self.R_load.scale * self.R_load.value + total_value)
        self.V_drop = total_value * I_total @ u_V

    def series_sum(self, values):
        return sum(values) @ u_Ohm

    def parallel_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    def current(self, voltage, value):
        return voltage / value

    def power(self, voltage, value):
        return voltage * voltage / value
        
    @property
    def part(self):
        if not self.DEBUG:
            part = Part('Device', 'R', footprint=self.footprint, dest=TEMPLATE)
            part.set_pin_alias('+', 1)
            part.set_pin_alias('-', 2)

            return part
        else:
            return None


    # @subcircuit
    def circuit(self):
        R_model = None

        if self.DEBUG:
            R_model = Build('R').spice
        else:
            R_model = self.part

    
        values = self.values_optimal(self.value, error=5) if not self.DEBUG else [self.value]
        resistors = []
        rin = Net()
        rout = Net()
        
        self.log(f'{self.value} implemented by {len(values)} resistors: ' + ', '.join([str(value) + " Ω" for value in values]))
        total_value = 0
        for index, value in enumerate(values):
            if type(value) == list:
                parallel_in = Net()
                parallel_out = Net()
                
                for resistance in value:
                    r = R_model(value=resistance)
                    r.ref = self.ref
                    total_value += resistance.value * resistance.scale
                        
                    r[1] += parallel_in
                    r[2] += parallel_out
                
                if index:
                    previous_r = resistors[-1]
                    previous_r[2] += parallel_in[1]

                resistors.append((None, parallel_in, parallel_out))

            else:
                r = R_model(value=value)
                total_value += value.value * value.scale
                r.ref = self.ref
                self.element = r
                        
                if index:
                    previous_r = resistors[-1]
                    previous_r[2] += r[1]
                
                resistors.append(r)

        self.value = total_value @ u_Ohm
        
        rin += resistors[0][1]
        rout += resistors[-1][2]
        
        self.input = rin
        self.output = rout

        self.input_n = self.output_n = self.gnd = Net()
        self.v_ref = Net()
       
        return 'Resistor'
