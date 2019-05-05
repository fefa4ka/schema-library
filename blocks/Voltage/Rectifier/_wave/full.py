from bem import Block, Diode
from skidl import Net, subcircuit


class Modificator(Block):
    """
        **Full-Wave Bridge**
        
        The entire input waveform is used. 
        
        The gaps at zero voltage occur because of the diodes’ forward voltage drop.
        
    """
    
    def create_bridge(self):
        D = Diode(type='generic') 
        
        load = {
            'V': self.V_out,
            'Load': self.Load
        }

        circuit = self.output_n & (
            (D(ref='D_out_n_in', **load)['A,K'] & self.input & D(ref='D_in_out', **load)['A,K']) 
            | (D(ref='D_out_n_in_n', **load)['A,K'] & self.input_n & D(ref='D_in_n_out', **load)['A,K']) 
        ) & self.output

   