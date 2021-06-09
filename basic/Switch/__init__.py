from bem.abstract import Electrical, Virtual
from bem import Net

from PySpice.Unit import u_Ohm, u_A, u_V


class Base(Electrical(port='two')):
    """# Switch
    
    Switch connected series to the signal.
    """

    pass

    # @property
    # def part(self):
    #     if self.SIMULATION:
    #         return

    #     return Part('Switch', 'SW_DPST', footprint=self.footprint, dest=TEMPLATE)

        # self.output += self.load.input
        # self.output_n += self.load.output

        # attach_load = self.output & self.load & self.output_n & self.gnd

        # if not self.SIMULATION:
        #     switch = self.part()
            
        #     self.input += switch['1,3']
        #     self.output += switch['2,4']
   
