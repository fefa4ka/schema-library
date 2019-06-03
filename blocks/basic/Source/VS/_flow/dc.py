from .. import Base
from bem import Build, u, u_V, u_s
from lcapy import Vdc
from sympy import Float

class Modificator(Base):
    def part_spice(self, *args, **kwargs):
        return Build('V').spice(*args, **kwargs)

    # def transfer(self, time=0 @ u_s):
    #     return Float(u(self.value))

    def network(self):
        return Vdc(self.V)
    
    def circuit(self):
        super().circuit(value=self.V)
    