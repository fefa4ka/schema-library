from .. import Base
from bem import Build, u_Ohm, u_A, u_V
from blocks.Abstract.Physical import Base as Physical
from skidl import Net, Part, TEMPLATE

class Modificator(Base, Physical):
    """**Physical Switch Input**
    
    Switch connected series to the signal.
    """

    def part_spice(self, *args, **kwargs):
        return Build('VCS').spice(*args, **kwargs)

    def part_template(self):
        part = Part('Switch', 'SW_DPST', footprint=self.footprint, dest=TEMPLATE)

        part.set_pin_alias('ip', 1)
        part.set_pin_alias('in', 3)
        part.set_pin_alias('op', 2)
        part.set_pin_alias('on', 4)

        return part

    def circuit(self):
        switch = self.part()

        # self.input += self.v_ref

        self.input += switch['ip']
        self.input_n += switch['in']
        
        self.output += switch['op']
        self.output_n += switch['on']

        super().circuit()