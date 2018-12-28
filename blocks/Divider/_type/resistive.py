from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_ms

class Modificator(Base):
    def power(self, voltage):
        return voltage * voltage / (self.R_in_value + self.R_out_value)

    def V_out_compute(self):
        return self.R_out_value * self.V_in / (self.R_in_value + self.R_out_value)
        
    @subcircuit
    def create_circuit(self, V_in, V_out):
        self.V_in = V_in
        self.V_out = V_out

        instance = self.clone
        instance.input = Net('DividerIn')
        instance.output = Net('DividerOut')
        instance.gnd = Net('DividerGround')

        R = Build('Resistor', **self.mods, **self.props).block

        self.R_in_value, self.R_out_value = 300, 300 #self.resistor_set()

        rin = R(value = self.R_in_value @ u_Ohm) 
        rout = R(value = self.R_out_value @ u_Ohm)

        circuit = instance.input & rin & instance.output & rout & instance.gnd
    
        return instance

    def test(self):
        super().test()

        waveforms = self.simulation.transient(step_time=0.5@u_ms, end_time=100@u_ms)  # Run a transient simulation from 0 to 10 msec.

        # Get the simulation data.
        time = waveforms.time                # Time values for each point on the waveforms.
        voltage = waveforms[self.node(self.input)]       # Get the voltage applied by the positive terminal of the source.
        voltage_out = waveforms[self.node(self.output)]  

        self.test_plot(Time_ms=time.as_ndarray() * 1000, V_in=voltage.as_ndarray(), V_out=voltage_out.as_ndarray(),
                       plots=[('Time_ms', 'V_in'), ('Time_ms', 'V_out')],
                       table=False)
        
