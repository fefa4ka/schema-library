from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_ms, u_Hz, u_A

class Modificator(Block):
    output_inverse = None

    @subcircuit
    def create_circuit(self, R_load=None, V_out=None, V_ripple=1 @ u_V, I_load=1 @ u_A, P_load=None, frequency=220 @ u_Hz):
        instance = super().create_circuit()
        
        instance.output_inverse = instance.output_gnd
        instance.output_gnd = Net('BridgeOutputGround')

        C = Build('Capacitor', **self.mods, **self.props).block

        if R_load and V_out:
            I_load = V_out / R_load
        
        C_value = I_load / (frequency * V_ripple)

        circuit =  instance.output & C(value=C_value @ u_F)['+', '-'] & instance.output_gnd & C(value=C_value @ u_F)['+', '-']  & instance.output_inverse
    
        return instance


    def test(self):
        super().test()

        waveforms = self.simulation.transient(step_time=0.5@u_ms, end_time=100@u_ms)  # Run a transient simulation from 0 to 10 msec.

        # Get the simulation data.
        time = waveforms.time                # Time values for each point on the waveforms.
        voltage = waveforms[self.node(self.input)]       # Get the voltage applied by the positive terminal of the source.
        voltage_out = waveforms[self.node(self.output)]  
        voltage_out_inv = waveforms[self.node(self.output_inverse)]  

        self.test_plot(Time_ms=time.as_ndarray() * 1000, V_in=voltage.as_ndarray(), V_out=voltage_out.as_ndarray(),  V_outInv=voltage_out_inv.as_ndarray(),
                       plots=[('Time_ms', 'V_in'), ('Time_ms', 'V_out'), ('Time_ms', 'V_outInv')],
                       table=False)