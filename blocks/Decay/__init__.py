from bem import Block, Build
from copy import copy
from settings import parts
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms
from math import log

class Base(Block):
    # Props
    V_in = 0
    V_out = 0
    Time_to_V_out = 0

    R_in_value = 0
    C_out_value = 0
       
    @subcircuit
    def create_circuit(self, V_in, V_out, Time_to_V_out, *args, **kwargs):
        self.V_in = V_in
        self.V_out = V_out
        self.Time_to_V_out = Time_to_V_out

        C_out_value = 0
        R_in_value = 0
        if kwargs.get('R_in_value', None):
            self.R_in_value = kwargs['R_in_value']
            R_in_value = self.R_in_value.value * self.R_in_value.scale

        if kwargs.get('C_out_value', None):
            self.C_out_value = kwargs['C_out_value']
            C_out_value = self.C_out_value.value * self.C_out_value.scale

        C = Build('Capacitor', **self.mods, **self.props).block
        R = Build('Resistor', **self.mods, **self.props).block

        Time_to_V_out = self.Time_to_V_out.value * self.Time_to_V_out.scale
        V_in = self.V_in.value * self.V_in.scale
        V_out = self.V_out.value * self.V_out.scale
        
        
        if self.R_in_value and not self.C_out_value:        
            self.C_out_value = (Time_to_V_out / (R_in_value * log(V_in / (V_in - V_out)))) @ u_F
        
        if self.C_out_value and not self.R_in_value:
            self.R_in_value = (Time_to_V_out / (C_out_value * log(V_in / (V_in - V_out)))) @ u_Ohm

        instance = copy(self)
        instance.input = Net("DecayInput")
        instance.output = Net("DecayOutput")
        instance.gnd = Net("DecayGround")

        rin = R(value = self.R_in_value @ u_Ohm)
        cout = C(value = self.C_out_value @ u_F).element
        route = instance.input & rin \
                            & instance.output \
                    & cout['+', '-'] \
                & instance.gnd

        return instance

    def test(self):
        super().test()

        # dc_vals = self.simulation.dc(VS=slice(0, 5, 0.5)) 
        # voltage = dc_vals[self.node(self.input)]       # Get the voltage applied by the positive terminal of the source.
        # voltage_out = dc_vals[self.node(self.output)]  
        # current = -dc_vals['VS']  # Get the current coming out of the positive terminal of the voltage source.
        
        waveforms = self.simulation.transient(step_time=self.Time_to_V_out / 10, end_time=self.Time_to_V_out * 10)  # Run a transient simulation from 0 to 10 msec.

        # Get the simulation data.
        time = waveforms.time                # Time values for each point on the waveforms.
        pulses = waveforms[self.node(self.input)]    # Voltage on the positive terminal of the pulsed voltage source.
        capacitor_voltage = waveforms[self.node(self.output)]  # Voltage on the capacitor.

        self.test_plot(Time_ms=time.as_ndarray() * 1000, V_pulses=pulses.as_ndarray(), V_capacitor=capacitor_voltage.as_ndarray(),
                       plots=[('Time_ms', 'V_pulses'), ('Time_ms', 'V_capacitor')],
                       table=False)
        
