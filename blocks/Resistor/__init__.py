
from bem import Block
from skidl import Part, Net, subcircuit, TEMPLATE
from PySpice.Unit import u_Ohm, u_V
import numpy as np
import logging

class Base(Block):
    def series_sum(self, values):
        return sum(values) @ u_Ohm

    def parallel_sum(self, values):
        return 1 / sum(1 / np.array(values)) @ u_Ohm

    def power(self, voltage):
        return voltage * voltage / self.value

    def min_change(self, V, C):
        table, solution = self.min_change_table(V, C)
        num_coins, coins = table[-1], []
        if num_coins == float('inf'):
            return []

        while C > 0:
            coins.append(V[solution[C]])
            C -= V[solution[C]]

        return coins

    def min_change_table(self, V, C):
        m, n = C+1, len(V)
        table, solution = [0] * m, [0] * m
        for i in range(1, m):
            minNum, minIdx = float('inf'), -1
            for j in range(n):
                if V[j] <= i and 1 + table[i - V[j]] < minNum:
                    minNum = 1 + table[i - V[j]]
                    minIdx = j
            table[i] = minNum
            solution[i] = minIdx

        return (table, solution)

    @property
    def part(self):
        part = Part('Device', 'R', footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('p', 1)
        part.set_pin_alias('n', 2)

        return part


    @subcircuit
    def create_circuit(self, value, variables=[]):
        R_model = None
        if self.DEBUG:
            from skidl.pyspice import R

            R_model = R
        else:
            R_model = self.part
        
        instance = self.clone
        instance.value = value
        if len(variables) > 1:
            variables = [int(unit.value * unit.scale) for unit in variables]
            value_Ohm = int(value.value * value.scale)
            values = self.min_change(variables, value_Ohm)
            resistors = []
            rin = Net()
            rout = Net()
            
            self.log(f'{value} implemented by {len(values)} resistors: ' + ', '.join([str(value) + " Ω" for value in values]))

            for index, value in enumerate(values):
                r = R(value = value @ u_Ohm)

                if index:
                    previous_r = resistors[-1]
                    previous_r[2] += r[1]
                
                resistors.append(r)
            
            rin += resistors[0][1]
            rout += resistors[-1][2]
            
            
            instance.input = rin
            instance.output = rout
        else:
            resistor = R_model(value=value)
            instance.element = resistor
            instance.input = instance.element['p']
            instance.output = instance.element['n']

        return instance
