from bem import Block
from bem import Voltage_Rectifier
from skidl import Net, subcircuit
from PySpice.Unit import u_ms, u_V, u_A, u_Hz, u_Ohm

class Base(Block):
    """**Voltage Double, Tripler, Quadrupler, etc**

    Voltage doubler. Think of it as *two half-wave rectifier circuits* in series. Variations of this circuit exist for voltage triplers, quadruplers, etc.

    You can extend this scheme as far as you want, producing what’s called a Cockcroft–Walton generator; these are used in arcane applications (such as particle accelerators) and in everyday applications (such as image intensifiers, air ionizers, laser copiers, and even bug zappers) that require a high dc voltage but hardly any current.

        * Paul Horowitz and Winfield Hill. "1.6.4 Rectifier configurations for power supplies" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 33-35
    """

    scale = 2

    V_ripple = 1 @ u_V

    frequency = 120 @ u_Hz

    def willMount(self, scale, frequency, V_ripple):
        self.scale = int(scale)
        
        self.load(self.V * self.scale)

    def circuit(self):
        HalfBridge = Voltage_Rectifier(wave='half', rectifier='full')
        
        sections = []
        
        if self.scale % 2:
            sections.append((self.input_n, self.input))
        else:
            sections.append((self.input, self.input_n))
        
        for block in range(self.scale):
            last = sections[-1]

            half = HalfBridge(V_out=self.V * self.scale, frequency=self.frequency, V_ripple=self.V_ripple, Load=self.Load)
            half.gnd += last[0]
            half.input += last[1]
            
            sections.append((half.input, half.output))

        self.output += sections[-1][1]
