from .. import Base
from bem.basic import Diode, Capacitor

from PySpice.Unit import u_uF

class Modificator(Base):
    """**DC Restoration**

    One interesting clamp application is “dc restoration” of a signal that has been ac coupled (capacitively coupled). Diagram shows the idea. This is particularly important for circuits whose inputs look like diodes (e.g., a transistor with grounded emitter); otherwise an ac-coupled signal will just fade away, as the coupling capacitor charges up to the signal’s peak voltage.
    """
    def circuit(self, *args, **kwargs):
        super().circuit(*args, **kwargs)

        D = Diode(type=='generic')
        C = Capacitor()
        
        signal = self.output
        self.output = Net('SignalClampedOutput')

        restoration = signal & C(value=1000 @ u_uF) & self.output & D(V=self.V, Load=self.Load)['K', 'A'] & self.gnd