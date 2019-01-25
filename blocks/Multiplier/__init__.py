from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_ms, u_V, u_A, u_Hz

class Base(Block):
    scale = 2

    def __init__(self, scale):
        self.scale = int(scale)

        self.circuit()

    @subcircuit
    def circuit(self):
        HalfBridge = Build('DiodeBridge', wave='half', rectifier='full').block

        self.input = Net()
        self.output = Net()
        self.gnd = self.input_n = self.output_n = Net()

        sections = []
        
        if self.scale % 2:
            sections.append((self.input_n, self.input))
        else:
            sections.append((self.input, self.input_n))
        
        for block in range(self.scale):
            last = sections[-1]

            half = HalfBridge()
            half.gnd += last[0]
            half.input += last[1]
            
            sections.append((half.input, half.output))

        self.output += sections[-1][1]
        