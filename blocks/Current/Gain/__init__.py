from bem import Block, Voltage_Divider, Transistor_Bipolar, Resistor, u, u_Ohm, u_V, u_A
from skidl import Net

class Base(Block):
    """**Emitter-Follower** Commin-Collector Amplifier
    
    The circuit shown here is called a common-collector amplifier, which has current gain but no voltage gain. It makes use of the emitter-follower arrangement but is modified to avoid clipping during negative input swings. The voltage divider (R1 and R2) is used to give the input signal (after passing through the capacitor) a positive dc level or operating point (known as the quiescent point). Both the input and output capacitors are included so that an ac input-output signal can be added without disturbing the dc operating point. The capacitors, as you will see, also act as filtering elements.”

    * Paul Scherz. “Practical Electronics for Inventors, Fourth Edition
    """
    
    V_ref = 15 @ u_V
    V_in = 10 @ u_V
    I_out = 0.015 @ u_A
    R_load = 1000 @ u_Ohm

    I_in = 0 @ u_A
    R_out = 0 @ u_Ohm
    Beta = 100
    V_base = 0 @ u_Ohm
    R_in = 0 @ u_Ohm
    

    def __init__(self, V_ref, V_in, I_out, R_load):
        self.V_ref = V_ref
        self.V_in = V_in
        self.I_out = I_out
        self.R_load = R_load
        self.input_n = None

        self.circuit()

    def circuit(self):
        R = Resistor()
        
        is_compensating = 'compensate' in self.mods.get('drop', [])
        self.gnd = Net()
        self.v_ref = Net()
        
        self.input =  self.output = Net()
       
        V_emitter = self.V_ref / 2
        self.R_out = (u(V_emitter) / u(self.I_out)) @ u_Ohm
        
        if is_compensating:
            self.R_out = self.R_out * 2
        
        
        amplifier = Transistor_Bipolar(
            type='npn',
            common='emitter',
            follow='emitter')(
                emitter = Resistor()(self.R_out)
            )
        
        Diode_drop = (amplifier.selected_part.spice_params.get('VJE', None) or 0.6) @ u_V
        self.V_base = V_emitter + Diode_drop
        self.Beta = amplifier.selected_part.spice_params.get('BF', self.Beta) 
        self.I_in = self.I_out / self.Beta
        
        # R_load = (u(self.V_base) / u(self.I_out)) @ u_Ohm
        # R_in_base = (self.Beta * ((u(self.R_out) * u(self.R_load)) / (u(self.R_out) + u(self.R_load)))) @ u_Ohm
        

        stiff_voltage = Voltage_Divider(type='resistive')(
            V_in = self.V_ref,
            V_out = self.V_base,
            I_out = self.I_in if is_compensating else self.I_in
        )
        stiff_voltage.gnd += self.gnd
        
        self.R_in = R.parallel_sum(R, [self.R_out, R.parallel_sum(R, [stiff_voltage.R_in, stiff_voltage.R_out]) / self.Beta])

        if is_compensating:
            R_ce = ((u(self.V_base)) / u(self.I_in)) @ u_Ohm
            compensator = Transistor_Bipolar(
                type='pnp',
                common='collector',
                follow='emitter')(
                    emitter = R(self.R_out)
                )
            compensator.v_ref += self.v_ref
            compensator.gnd += self.input_n or self.gnd

            compensated = Net('CurrentGainCompensation')
            rc = self.v_ref & stiff_voltage & self.input & compensator & compensated
            self.output = compensated
        else:
            rc = self.v_ref & stiff_voltage & self.input
    
        amplified = Net('CurrentGainOutput')
        amplifier.v_ref += self.v_ref
        amplifier.gnd += self.input_n or self.gnd
        gain = self.output & amplifier & amplified 

        self.output = amplified
