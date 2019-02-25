from bem import Block, Build, u_V, u_A
from skidl import Part, TEMPLATE


class Base(Block):
    props = {
        'type': ['generic', 'zener', 'shockley', 'led', 'photo']
    }
    
    V_in = 5 @ u_V
    I_in = 0.5 @ u_A
    def __init__(self, V_in=None, I_in=None):
        self.V_in = V_in or self.V_in
        self.I_in = I_in or self.I_in

        if not self.props.get('type', None):
            self.props['type'] = 'generic'

        if self.selected_part and self.selected_part.model:
            self.model = self.selected_part.model
        else:  
            self.model = 'D'
        
        super().__init__()

    @property
    def spice_part(self):
        return Build('D').spice

    @property
    def part(self):
        if self.DEBUG:
            return

        if self.model == 'D':
            library = 'Device'
        else:
            library = 'Diode'

        part = Part(library, self.selected_part.scheme or self.model, footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('A', 1)
        part.set_pin_alias('K', 2)
        
        return part
