from bem import Block, Build
from skidl import Net, subcircuit


class Modificator(Block):
    @subcircuit
    def create_bridge(self):
        D = Build('Diode').block
    
        circuit = self.input & D()['A,K'] & self.output

    @subcircuit
    def create_circuit(self, **kwargs):
        instance = super().create_circuit(**kwargs)

        instance.gnd += instance.output_gnd

        return instance
