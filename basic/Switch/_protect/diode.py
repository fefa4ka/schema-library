from .. import Base
from bem.basic import Diode

class Modificator(Base):
    """**Suppression Diode**

    Protect the transistor with a diode across the load.
 
    """

    def circuit(self):
        super().circuit()
        
        if 'on' in self.mods['on_press']:
            protect = self.load_block.input & Diode(type='generic')(**self.load_args)['K,A'] & self.load_block.output
        
        if 'off' in self.mods['on_press']:
            protect = self.load_block.input & Diode(type='generic')(**self.load_args)['A,K'] & self.load_block.output
