from bem import Block, RLC
from settings import parts
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_A, u_s
from math import log

class Base(Block):
    """**Decay to equilibrium**
    
    The product RC is called the time constant of the circuit. For `R_s` in ohms and `C_g` in farads, the product RC is in seconds. A `C_g` microfarad across `R_s` 1.0k has a time constant Time_to_`V_(out)` of 1 ms; if the capacitor is initially charged to `V_(out) = 1.0 V`, the initial current `I_(out)` is 1.0 mA.

    At time `t = 0`, someone connects the battery. The equation for the circuit is then 
    
    `I = C * (dV) / (dT) = (V_(i\\n) - V_(out)) / R_s` 
    
    with solution

    `V_(out) = V_(i\\n) + A * e ^ (-t / (R_s * C_g))`

    The constant `A` is determined by initial conditions: `V_(out) = 0` at `t = 0`; therefore, `A = −V_(i\\n)`, and 
    
    `V_(out) = V_(i\\n) * (1 − e ^ (−t / (R_s * C_g)))`

    Once again there’s good intuition: as the capacitor charges up, the slope (which is proportional to current, because it’s a capacitor) is proportional to the remaining voltage (because that’s what appears across the resistor, producing the current); so we have a waveform whose slope decreases proportionally to the vertical distance it has still to go an exponential.

    To figure out the time required to reach a voltage `V_(out)` on the way to the final voltage `V_(i\\n)`: 
    
    `t = R * C * log_e(V_(i\\n) / (V_(i\\n) - V_(out)))`

    * Paul Horowitz and Winfield Hill. "1.4.2 RC circuits: V and I versus time" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 21-23
    """
    V_in = 10 @ u_V
    V_out = 5 @ u_V
    I_out = 0.5 @ u_A
    Time_to_V_out = 0.005 @ u_s

    R_in = 0 @ u_Ohm
    C_out = 0 @ u_Ohm

    def __init__(self, V_in, V_out, I_out, Time_to_V_out):
        self.V_in = V_in
        self.V_out = V_out
        self.Time_to_V_out = Time_to_V_out

        self.circuit()

    # @subcircuit
    def circuit(self):
        R_in_value = self.R_in.value * self.R_in.scale
        C_out_value = self.C_out.value * self.C_out.scale

        if not (R_in_value and C_out_value):
            self.R_in = (self.V_in / self.I_out) @ u_Ohm
            R_in_value = self.R_in.value * self.R_in.scale

        Time_to_V_out = self.Time_to_V_out.value * self.Time_to_V_out.scale
        V_in = self.V_in.value * self.V_in.scale
        V_out = self.V_out.value * self.V_out.scale
        
        if R_in_value and not C_out_value:        
            self.C_out = (Time_to_V_out / (R_in_value * log(V_in / (V_in - V_out)))) @ u_F
        
        if C_out_value and not R_in_value:
            self.R_in = (Time_to_V_out / (C_out_value * log(V_in / (V_in - V_out)))) @ u_Ohm
        
        rlc = RLC(series=['R'], gnd=['C'])(
            R_series = self.R_in,
            C_gnd = self.C_out
        )
        
        self.input = self.v_ref = rlc.input
        self.output = rlc.output
        self.gnd = rlc.gnd
