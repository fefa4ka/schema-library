from .. import Base
from bem import u_m, u_V, u_A
from bem.basic import Resistor

class Modificator(Base):
    color = 'green'
    # wavelength = 535e-9 @ u_m
    # wavelength_range = 35e-9 @ u_m
    V = 3.4 @ u_V
    Load = 20e-3 @ u_A
    V_min = 1.9 @ u_V

    def willMount(self, color):
        self.load(self.V)