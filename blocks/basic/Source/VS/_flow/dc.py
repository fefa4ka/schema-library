from .. import Base
from bem import Build, u, u_V, u_s
from lcapy import Vdc
from sympy import Float

class Modificator(Base):
    value = 5 @ u_V

    def willMount(self, value):
        pass
        
    def part_spice(self, *args, **kwargs):
        return Build('V').spice(*args, **kwargs)

    def transfer(self, time=0 @ u_s):
        return Float(u(self.value))

    def network(self):
        return Vdc(self.value)
    
    def circuit(self):
        super().circuit(value=self.value)