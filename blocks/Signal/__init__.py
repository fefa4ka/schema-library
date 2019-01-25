from bem import Block, Build
from skidl import Net, subcircuit
# from PySpice.Unit import u_kOhm, u_V

class Base(Block):
    def __init__(self, input=None):
        self.input = input

        self.circuit()

    
    def circuit(self):
        self.input = self.output = self.input or Net('SignalInput')

        self.v_ref = Net()
        self.gnd = Net()