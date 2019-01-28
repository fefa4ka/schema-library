from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A

class Modificator(Base):
    """**Diode Voltage Clamp**
    
    Sometimes it is desirable to limit the range of a signal (i.e., prevent it from exceeding certain voltage limits) somewhere in a circuit.
    
    A voltage divider can provide the reference voltage for a clamp. In this case you must ensure that the resistance looking into the voltage divider (`I_out`) is small compared with `R_load`.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    """

    V_signal = 4 @ u_V
    V_ref = 10 @ u_V
    I_ref = 0.5 @ u_A
    R_load = 100 @ u_Ohm

    def __init__(self, V_signal=None, V_ref=None, I_ref=None, R_load=None, *args, **kwargs):
        self.V_signal = V_signal
        self.V_ref = V_ref
        self.I_ref = I_ref
        self.R_load = R_load

        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()

        D = Build('Diode').block
        R = Build('Resistor').block
        Divider = Build('Divider', type='resistive').block
        
        signal = self.output
        self.output = Net('SignalClampedOutput')

        Rref = None
        if self.V_ref and self.V_signal and self.V_ref > self.V_signal:
            Rref = Divider(V_in=self.V_ref, V_out=self.V_signal, I_out=self.I_ref)
            Rref.gnd += self.gnd
        else:
            pass
            Rref = R(667 @ u_Ohm)

        clamp = self.v_ref & Rref & D()['K', 'A'] & self.output
        signal_input = signal & R(value=self.R_load, ref='R_load') & self.output
        
    def test_sources(self):
        return super().test_sources() + [{
                'name': 'V',
                'args': {
                    'value': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_ref'],
                    'n': ['gnd']
                }
        }]