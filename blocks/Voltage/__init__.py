from bem import Block, u_Ohm, u, u_V, u_A
from skidl import Net

class Base(Block):
    """**Voltage Manipulator**

    """
        

    def circuit(self):
        self.input = self.output = Net("VoltageInput")
        self.gnd = self.input_n = self.output_n = Net()
        self.v_ref = Net()
        