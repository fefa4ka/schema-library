from .. import Base
from bem import u, u_m, u_V, u_A
from bem.basic import Resistor
from skidl import Net

class Modificator(Base):
    # wavelength = 535e-9 @ u_m
    # wavelength_range = 35e-9 @ u_m


    def willMount(self, color='green'):
        """
        V_min -- Minimal voltage that could be applied
        """

    def init_params(self):
        self.Power = u(self['I_load']) @ u_A
        self.V_j = u(self['V_drop']) @ u_V

        self.consumption(self.V_j)
        self.Z = (self.V_j * self.V_j) / self.P
        self.load(self.V - self.V_j)

        if self.V < self['V_min']:
            self.error(AssertionError, "V = %s should be greater than V_min = %s" % (self.V, self.V_min))
