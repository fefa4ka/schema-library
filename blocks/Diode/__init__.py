from bem import Block, Build, u_V, u_A
from skidl import Part, TEMPLATE


class Base(Block):
    """
    A diode is a two-terminal electronic component that conducts current primarily in one direction (asymmetric conductance); it has low (ideally zero) resistance in one direction, and high (ideally infinite) resistance in the other.

    The most common function of a diode is to allow an electric current to pass in one direction (called the diode's forward direction), while blocking it in the opposite direction (the reverse direction). As such, the diode can be viewed as an electronic version of a check valve. This unidirectional behavior is called rectification, and is used to convert alternating current (ac) to direct current (dc). Forms of rectifiers, diodes can be used for such tasks as extracting modulation from radio signals in radio receivers.

    However, diodes can have more complicated behavior than this simple on–off action, because of their nonlinear current-voltage characteristics. Semiconductor diodes begin conducting electricity only if a certain threshold voltage or cut-in voltage is present in the forward direction (a state in which the diode is said to be forward-biased). 

    """
    props = {
        'type': ['generic', 'zener', 'shockley', 'led', 'photo']
    }

    spice_params = {
        'AF': {'description': 'Flicker noise exponent', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'BV': {'description': 'Reverse breakdown voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'CJO': {'description': 'Zero-bias junction capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'EG': {'description': 'Band-gap energy', 'unit': { 'suffix': 'eV', 'name': 'electron volt' }, 'value': ''},
        'FC': {'description': 'Coefficient for forward-bias', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'IBV': {'description': 'Current at breakdown voltage', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'IS': {'description': 'Saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'KF': {'description': 'Flicker noise coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'M': {'description': 'Grading coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'N': {'description': 'Emission coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'RS': {'description': 'Ohmic resistanc', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'TNOM': {'description': 'Parameter measurement temperature', 'unit': { 'suffix': '°', 'name': 'degree' }, 'value': ''},
        'TT': {'description': 'Transit-time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': ''},
        'VJ': {'description': 'Junction potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'XTI': {'description': 'Saturation-current temp.exp', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''}
    }
    
    
    V_in = 5 @ u_V
    
    def __init__(self, V_in=None, Load=None, *args, **kwargs):
        self.V_in = V_in or self.V_in
        self.Load = Load

        if not self.props.get('type', None):
            self.props['type'] = 'generic'

        if self.selected_part and self.selected_part.model:
            self.model = self.selected_part.model
        else:  
            self.model = 'D'
        
        super().__init__(*args, **kwargs)

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
