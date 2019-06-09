from .. import Base
from bem import Build, u, u_V, u_s
from lcapy import Vdc
from sympy import Float

class Modificator(Base):
    # def transfer(self, time=0 @ u_s):
    #     return Float(u(self.value))

    def network(self):
        return Vdc(self.V)
    
    def circuit(self):
        super().circuit(value=self.V)
    
    def devices(self):
        return {
            'ka3005d': {
                'title': 'Laboratory Power Supply',
                'port': 'serial',
                'channels': []
            }
        }
