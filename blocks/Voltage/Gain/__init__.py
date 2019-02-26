from bem import Block, Transistor_Bipolar, Voltage_Divider, Resistor, Capacitor, u, u_F, u_Ohm, u_V, u_Hz, u_A
from math import pi
from skidl import Net

class Base(Block):
    """**Common-Emitter Amplifier**
    
    The circuit shown here is known as a common-emitter amplifier. Unlike the common-collector amplifier, the common-emitter amplifier provides voltage gain. This amplifier makes use of the common-emitter arrangement and is modified to allow for ac coupling.

    * Paul Scherz. “Practical Electronics for Inventors, Fourth Edition
    """

    V_ref = 20 @ u_V
    V_in = 1.4 @ u_V
    f_3db = 120 @ u_Hz
    I_quiescent = 0.1 @ u_A

    gain = 0
    C_in = 0 @ u_F
    R_c = 0 @ u_F
    R_e = 0 @ u_F
    
    # I_e = 0 @ u_A
    # I_c = 0 @ u_A
    V_stiff = 0 @ u_V

    def __init__(self, V_ref, V_in, f_3db, I_quiescent):
        self.V_ref = V_ref
        self.V_in = V_in
        self.f_3db = f_3db
        self.I_quiescent = I_quiescent

        self.gain = self.V_ref / self.V_in

        self.circuit()

    def circuit(self):
        self.input = self.output = Net('VoltageGainInput')
        self.v_ref = Net('Vref')
        self.gnd = Net()

        self.V_stiff = 1.6 @ u_V # self.V_in if u(self.V_in) > 1.6 else 1.6 @ u_V
        
        self.R_e = ((u(self.V_stiff) - 0.6) / u(self.I_quiescent)) @ u_Ohm
        self.R_c = self.gain * self.R_e

        R = Resistor()

        amplifier = Transistor_Bipolar(
            common='emitter',
            follow='collector'
        )(
            collector = R(self.R_c),
            emitter = R(self.R_e)
        )

        stiff_voltage = Voltage_Divider(type='resistive')(
            V_in = self.V_ref,
            V_out = self.V_stiff,
            I_out = self.I_quiescent
        )

        stiff_voltage.input += self.v_ref

        self.C_in = (1 / (2 * pi * self.f_3db * R.parallel_sum(R, [stiff_voltage.R_in, stiff_voltage.R_out]))) @ u_F

        
        amplified = Net('VoltageGainOutput')

        circuit = stiff_voltage & self & amplifier & amplified
        
        signal = Net('VoltageGainAcInput')
        ac_coupling = signal & Capacitor()(self.C_in) & self.input
        self.input = signal
        self.output = amplified
