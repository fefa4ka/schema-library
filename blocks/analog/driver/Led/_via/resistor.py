from .. import Base
from bem.basic import Resistor

class Modificator(Base):
    def circuit(self):
        for led in self.diodes:
            led.load(self.V - led.V_j)
            driver = self.v_ref & Resistor()(led.R_load) & led & self.gnd
