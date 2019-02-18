from .. import Base
from bem import Diode

class Modificator(Base):
    """**Suppression Diode**

    Protect the transistor with a diode across the load.
 
    """

    def circuit(self):
        super().circuit()
        
        if 'on' in self.mods['on_press']:
            protect = self.load.input & Diode()()['K,A'] & self.load.output
        
        if 'off' in self.mods['on_press']:
            protect = self.load.input & Diode()()['A,K'] & self.load.output