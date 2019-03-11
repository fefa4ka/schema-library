
from blocks.Abstract.Combination import Base as Block
from skidl import Part, Net, subcircuit, TEMPLATE
from PySpice.Unit import u_Ohm, u_V, u_W, u_A
import numpy as np
from bem import Build, u
import logging

class Base(Block):
    """Resistor
    
    Generic resistance. 
    Resistance implemented by combination of series or parallel connected resistors from available values in stock. 
    """

    increase = True
    value = 1000 @ u_Ohm
    V_in = 10 @ u_V
    G = 0
    P = 0 @ u_W
    I = 0 @ u_A
    V_drop = 0 @ u_V

    ref = 'R'

    def __init__(self, value, V_in=None, Load=0.1 @ u_Ohm, *args, **kwargs):
        """
            value -- A resistor is made out of some conducting stuff (carbon, or a thin metal or carbon film, or wire of poor conductivity), with a wire or contacts at each end. It is characterized by its resistance.
            V_drop -- Voltage drop after resistor with Load 
            G -- Conductance `G = 1 /R`
        """

        if type(value) in [str, int, float]:
            value = float(value) @ u_Ohm

        self.value = value
        self.Load = Load

        self.calculator()

        super().__init__(*args, **kwargs)
    
    def calculator(self):
        # Power Dissipation
        value = u(self.value)

        V_in_value = u(self.V_in)
        self.P = self.power(V_in_value, value) @ u_W
        self.I = self.current(V_in_value, value) @ u_A
        if self.Load.is_same_unit(1 @ u_Ohm):
            I_total = self.current(V_in_value, u(self.Load + self.value))
        elif self.Load.is_same_unit(1 @ u_A):
            I_total = self.I + self.load
        elif self.Load.is_same_unit(1 @ u_W):
            I_total = (self.P + self.load) / V_in_value
        
        self.V_drop = (value * I_total) @ u_V
        self.G = 1 / value
        self.load(self.V_in - self.V_drop)

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
