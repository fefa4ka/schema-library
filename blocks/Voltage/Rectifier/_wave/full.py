from bem import Block, Diode
from skidl import Net, subcircuit


class Modificator(Block):
    def create_bridge(self):
        D = Diode()
        
        circuit = self.output_n & (
            (D()['A,K'] & self.input & D()['A,K']) 
            | (D()['A,K'] & self.input_n & D()['A,K']) 
        ) & self.output

   