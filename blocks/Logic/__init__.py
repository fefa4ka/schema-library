from bem import Block, Build
from skidl import Net, subcircuit


class Base(Block):
    inputs = []
    outputs = []

    def __init__(self, inputs=None):
        default_input = [Net()]
        if self.DEBUG:
            self.input_b = Net()
            default_input = [Net(), self.input_b]

        self.inputs = self.outputs = inputs or default_input

        self.circuit()

    def circuit(self):
        
        self.v_ref = Net()
        self.gnd = Net()

    @property
    def input(self):
        return self.inputs[0]

    @property
    def output(self):
        return self.outputs[0]
