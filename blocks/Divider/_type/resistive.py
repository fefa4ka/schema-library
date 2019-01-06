from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_ms

class Modificator(Base):
    def power(self, voltage):
        return voltage * voltage / (self.R_in_value + self.R_out_value)

    def V_out_compute(self):
        return self.R_out_value * self.V_in / (self.R_in_value + self.R_out_value)
        
    @subcircuit
    def create_circuit(self, V_in, V_out):
        self.V_in = V_in
        self.V_out = V_out

        instance = self.clone
        instance.input = Net('DividerIn')
        instance.output = Net('DividerOut')
        instance.gnd = Net()

        R = Build('Resistor', **self.mods, **self.props).block

        self.R_in_value, self.R_out_value = 0.5, 0.5 #self.resistor_set()

        rin = R(value = self.R_in_value @ u_Ohm) 
        rout = R(value = self.R_out_value @ u_Ohm)

        circuit = instance.input & rin & instance.output & rout & instance.gnd
    
        return instance