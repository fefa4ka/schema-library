from .. import Base
from skidl import subcircuit
from skidl.pyspice import u_Ohm

class Modificator(Base):
    @subcircuit
    def make(self, input, output):
        R, gnd = self.part['R'], self.part['gnd']

        R_in_value, R_out_value = 3, 4 #self.resistor_set()

        rin = R(value = R_in_value @ u_Ohm) 
        rout = R(value = R_out_value @ u_Ohm)
        route = input & rin \
                            & output \
                    & rout \
                & gnd
