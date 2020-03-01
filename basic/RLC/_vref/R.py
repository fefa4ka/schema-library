from .. import Base
from bem.basic import Resistor
from bem import Net
from PySpice.Unit import u_Ohm

class Modificator(Base):
    R_vref = 1 @ u_Ohm

    def willMount(self, R_vref):
        pass

    def circuit(self):
        super().circuit()

        signal = None
        if not (self.input and self.output):
            signal = self.input = Net('RLCInput')
            self.output = Net('RLCOutput')
        else:
            signal = self.output
            self.output = Net('VrefResistorOutput')


        R_out = Resistor()(value=self.R_vref, ref='R_v', **self.load_args)

        circuit = self.v_ref & R_out & self.output & signal
