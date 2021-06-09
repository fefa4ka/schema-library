from .. import Base
from bem.basic import Resistor, Diode

class Modificator(Base):
    def wire_input(self, up, down):
        upper_eliminator = self.v_ref & Resistor()(self.R_load * up.Beta) & Diode(type='generic')() & self.input
        lower_eliminator = self.input & Diode(type='generic')() & Resistor()(self.R_load * down.Beta) & self.v_inv

        eliminator = self.input & Resistor()(100, V=0.1) & self.output
        super().wire_input(up, down)
