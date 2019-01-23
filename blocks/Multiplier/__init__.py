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
        self.gnd = Net()

        sections = []
        
        if self.scale % 2:
            sections.append((self.gnd, self.input))
        else:
            sections.append((self.input, self.gnd))
        
        for block in range(self.scale):
            last = sections[-1]

            half = HalfBridge()
            half.gnd += last[0]
            half.input += last[1]
            
            sections.append((half.input, half.output))

        self.output += sections[-1][1]
        