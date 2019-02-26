from .. import Base
from bem import Divider, Resistor, Diode, u, u_Ohm, u_V, u_A
from skidl import Net, subcircuit


class Modificator(Base):
    """**Diode Voltage Clamp**
    
    Sometimes it is desirable to limit the range of a signal (i.e., prevent it from exceeding certain voltage limits) somewhere in a circuit.
    
    A voltage divider can provide the reference voltage for a clamp. In this case you must ensure that the resistance looking into the voltage divider (`I_out`) is small compared with `R_load`.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    """

    V_ref = 10 @ u_V
    V_out = 3 @ u_V
    I_ref = 0.01 @ u_A
    R_load = 1000 @ u_Ohm

    def __init__(self, V_ref=None, V_out=None, I_ref=None, R_load=None, *args, **kwargs):
        self.V_ref = V_ref
        self.V_out = V_out
        self.R_load = R_load

        # if R_load:
        # self.I_ref = u(V_out) / u(I_ref) @ u_Ohm
        # self.R_load =( u(V_out) / u(I_ref)) @ u_Ohm
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalClampedOutput')

        Rref = None
        if self.V_out and self.V_ref and self.V_ref >  self.V_out:
            Rref = Divider(type='resistive')(
                V_in = self.V_ref,
                V_out = self.V_out,
                I_out=self.I_ref)
            Rref.gnd += self.gnd
        else:
            Rref = Resistor()(667)

        clamp = self.v_ref & Rref & Diode()()['K', 'A'] & self.output
        signal_input = signal & Resistor()(self.R_load, ref='R_load') & self.output
