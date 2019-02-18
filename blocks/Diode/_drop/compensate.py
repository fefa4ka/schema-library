from .. import Base
from skidl import Net
from bem import Diode, Capacitor, Resistor, u_pF, u_kOhm

class Modificator(Base):
    """**Compensating Diode Forward Voltage Drop*
 
    """

    def circuit(self):
        super().circuit()
        
        R = Resistor()
        C = Capacitor()
        D = Diode()

        signal = self.input
        # self.input = Net('CompensationOutput')

        compensator = self.input & C(100 @ u_pF) & signal
        ref = Net('CompensationDropVref')
        
        compensator_ref = ref & R(1 @ u_kOhm) & self.v_ref
        compensator = signal & R(1 @ u_kOhm) & ref & D()['A,K'] & self.gnd
        after_pull = self.output & R(1 @ u_kOhm) & self.gnd
        
        