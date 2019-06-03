from bem.basic import Resistor, Capacitor
from bem.basic.transistor import Bipolar
from bem.analog.voltage import Divider
from bem import Net, u, u_Ohm, u_V, u_A, u_F, u_Hz
from math import pi
from .. import Base

class Modificator(Base):
    """**Unity-gain phase splitter**
    
    Sometimes it is useful to generate a signal and its inverse, i.e., two signals 180◦ out of phase. That’s easy to do – just use an emitter-degenerated amplifier with a gain of −1.

    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 88-89
    """

    V_ref = 20 @ u_V
    f_3db = 120 @ u_Hz
    
    V_split = 0 @ u_V
    R_out = 0 @ u_Ohm
    C_in = 0 @ u_F
    I_b = 0.001 @ u_A

    def willMount(self, V_ref, f_3db):
        """
            f_3db -- Frequencies of interest are passed by the highpass filter
            C_in -- Blocking capacitor is chosen so that all frequencies of interest are passed by the highpass filter `C_(i\\n) >= 1 / (2 pi f_(3db) (R_s∥R_g))`
        """
        
        self.V_split = self.V_ref / 6
        self.R_out = (u(self.V_split) / u(self.I_b) * 100) @ u_Ohm

        self.load(V_ref)
    
    def circuit(self):
        super().circuit()
        
        R = Resistor()
        stiff_voltage = Divider(type='resistive')(
            V = self.V_ref,
            V_out = self.V_split + 0.6 @ u_V,
            Load = self.I_b
        )  
        stiff_voltage.input += self.v_ref
        stiff_voltage.gnd += self.gnd
        stiff_voltage.v_ref += self.v_ref

        splitter = Bipolar(
            type='npn',
            common='emitter',
            follow='collector'
        )(
            collector = R(self.R_out, ref='R_c', **self.load_args),
            emitter = R(self.R_out, ref='R_e', **self.load_args)
        )
        
        split = stiff_voltage & self & splitter
        self.output = Net('OutputInverse')
        self.output_n += splitter.collector
        self.output += splitter.emitter
        R_in = R.parallel(R, [self.R_out * 2, stiff_voltage.R_in, stiff_voltage.R_out]).Z.evaluate() @ u_Ohm
        
        self.C_in = (1 / (2 * pi * self.f_3db * R_in)) @ u_F
        
        signal = Net('VoltageShiftAcInput')
        ac_coupling = signal & Capacitor()(self.C_in, ref='C_in', **self.load_args) & self.input
        self.input = signal


