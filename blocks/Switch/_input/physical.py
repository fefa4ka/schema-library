from .. import Base
from skidl import Net, subcircuit, Part
from PySpice.Unit import u_Ohm, u_A, u_V


class Modificator(Base):
    """**Physical Switch Input**
    
    Switch connected series to the signal.
    """


    @property
    def part(self):
        if self.DEBUG:
            return

        return Part('Switch', 'SW_DPST', footprint=self.footprint, dest=TEMPLATE)

    def circuit(self):
        switch = self.part()
        
        self.input += switch['1,3']
        self.output += switch['2,4']
