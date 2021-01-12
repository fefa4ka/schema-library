from skidl import Net
from bem.basic import Diode, Capacitor

from PySpice.Unit import u_uF


class Modificator:
    """**DC Restoration**

    One interesting clamp application is “dc restoration” of a signal that has been ac coupled (capacitively coupled). Diagram shows the idea. This is particularly important for circuits whose inputs look like diodes (e.g., a transistor with grounded emitter); otherwise an ac-coupled signal will just fade away, as the coupling capacitor charges up to the signal’s peak voltage.
    """
    def circuit(self, *args, **kwargs):
        super().circuit(*args, **kwargs)

        signal = self.output
        self.output = Net('SignalClampedOutput')

        restoration = signal & Capacitor()(value=1 @ u_uF) & self.output & Diode(type='generic')()['K', 'A'] & self.gnd
