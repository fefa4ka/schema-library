from bem import u_V, u_s
from bem.analog.voltage import Decay

class Modificator:
    def circuit(self):
        super().circuit()

        decay = Decay()(V_out=self.V * 0.9, Time_to_V_out=0.1 @ u_s)

        decay.gnd & self.gnd

        reset_delay = self.v_ref & decay & self['RESET']
