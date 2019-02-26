from bem import Block, Diode
from skidl import Net, subcircuit


class Modificator(Block):
    def create_bridge(self):
        D = Diode()
    
        circuit = self.input & D()['A,K'] & self.output

    def circuit(self, **kwargs):
        super().circuit(**kwargs)

        self.output_n = self.input_n = self.gnd
