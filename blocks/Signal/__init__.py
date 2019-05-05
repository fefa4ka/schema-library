from bem import Block, Build, u_V
from skidl import Net, subcircuit
# from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Block):
    V = 10 @ u_V

    def willMount(self, input=None):
        self.input = input
    
    def circuit(self):
        self.input = self.output = self.input or Net('SignalInput')

        self.v_ref = Net()
        self.gnd = Net()