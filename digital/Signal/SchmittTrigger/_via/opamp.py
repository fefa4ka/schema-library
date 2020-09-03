from .. import Base
from bem.basic import OpAmp, Resistor
from bem.analog.voltage import Divider


class Modificator(Base):
    def willMount(self):
        trigger = OpAmp()()

        # If symmetrical
        if self.V_on + self.V_off == 0:
            threshold = Resistor()(self.R_load * 10)
        else:
            threshold = Divider(type='resistive')(V_out=self.V_on, I_load=self.I_load / 10)
            threshold.value = threshold.R_in + threshold.R_out

        hysteresis = Resistor()(threshold.value * self.V / abs(self.V_on))

        trigger.v_inv & self.v_inv
        self.gnd & trigger.gnd & threshold.gnd
        self.input & trigger.input_n
        self.v_ref & threshold & trigger.input
        trigger.input & hysteresis & trigger.output & self.output


