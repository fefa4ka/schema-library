from bem import Block, Build
from skidl import Net, subcircuit


class Modificator(Block):
    @subcircuit
    def create_bridge(self):
        D = Build('Diode').block
        
        circuit = self.output_gnd & (
            (D()['A,K'] & self.input & D()['A,K']) 
            | (D()['A,K'] & self.gnd & D()['A,K']) 
        ) & self.output