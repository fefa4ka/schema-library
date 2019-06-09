from .. import Base
from bem import u_V, u_s
from bem.analog.voltage import Decay

class Modificator(Base):
    def circuit(self):
        super().circuit()
     
        decay = Decay()(V_out = 4.5 @ u_V, Time_to_V_out = 0.1 @ u_s)
        decay.gnd = self.gnd

        reset_delay = self.v_ref & decay & self['RESET']
