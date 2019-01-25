from bem import Block, Build
from skidl import Net, subcircuit


class Modificator(Block):
    #@subcircuit
    def create_bridge(self):
        D = Build('Diode').block
    
        circuit = self.input & D()['A,K'] & self.output

    #@subcircuit
    def circuit(self, **kwargs):
        super().circuit(**kwargs)

        self.output_n = self.input_n = self.gnd
