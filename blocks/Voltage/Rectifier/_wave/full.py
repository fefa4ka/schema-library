from bem import Block, Diode
from skidl import Net, subcircuit


class Modificator(Block):
    """
        **Full-Wave Bridge**
        
        The entire input waveform is used. 
        
        The gaps at zero voltage occur because of the diodes’ forward voltage drop.
        
    """
    
    def create_bridge(self):
        D = Diode()
        
        circuit = self.output_n & (
            (D(ref='D_out_n_in')['A,K'] & self.input & D(ref='D_in_out')['A,K']) 
            | (D(ref='D_out_n_in_n')['A,K'] & self.input_n & D(ref='D_in_n_out')['A,K']) 
        ) & self.output

   