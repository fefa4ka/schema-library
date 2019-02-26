from bem import Block, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_A, u_V

class Base(Block):
    """**Switch**
    
    Switch connected series to the signal.
    """

    V_ref = 15 @ u_V
    V_input = 10 @ u_V
    I_load = 0.015 @ u_A

    load = None

    def __init__(self, V_ref=None, V_input=None, I_load=None, load=None, *args, **kwargs):
        if not self.gnd:
            self.gnd = Net()

        if self.DEBUG:
            self.load = Resistor()(value = 330, ref = 'R_switch_load')
        else:
            self.load = load
        
        self.input = Net('SwitchController')
        self.output = Net('SwitchLoadP')
        self.output_n = Net('SwitchLoadN')
        self.v_ref = Net() # ?
        
        self.circuit(*args, **kwargs)

    # @property
    # def part(self):
    #     if self.DEBUG:
    #         return

    #     return Part('Switch', 'SW_DPST', footprint=self.footprint, dest=TEMPLATE)

        # self.output += self.load.input
        # self.output_n += self.load.output

        # attach_load = self.output & self.load & self.output_n & self.gnd

        # if not self.DEBUG:
        #     switch = self.part()
            
        #     self.input += switch['1,3']
        #     self.output += switch['2,4']
   