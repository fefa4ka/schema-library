from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_uF, u_H, u_kHz

class Base(Block):
    emitter = None
    base = None
    collector = None

    props = {
        'type': ['npn', 'pnp'],
        'common': ['emitter', 'base', 'collector'],
        'follow': ['emitter', 'base', 'collector']
    }

    spice_params = {
        'BF': {'title': 'β_f', 'description': 'Ideal maximum forward beta', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'BR': {'description': 'Ideal maximum reverse beta', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'CJC': {'description': 'Base-collector zero-bias p-n capacitance',
                'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'CJE': {'description': 'Base-emitter zero-bias p-n capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'EG': {'description': 'Bandgap voltage (barrier height)', 'unit': { 'suffix': 'eV', 'name': 'eV' }, 'value': ''},
        'FC': {'description': 'Forward-bias depletion capacitor coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'IKF': {'description': 'Corner for forward-beta high-current roll-off',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'IKR': {'description': 'Corner for reverse-beta high-current roll-off',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'IS': {'description': 'Transport saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'ISC': {'description': 'Base-collector leakage saturation current',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'ISE': {'description': 'Base-emitter leakage saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'ITF': {'description': 'Transit time dependency on Ic', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'MJC': {'description': 'Base-collector p-n grading factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'MJE': {'description': 'Base-emitter p-n grading factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'NC': {'description': 'Base-collector leakage emission coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'NE': {'description': 'Base-emitter leakage emission coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'NK': {'description': 'High-current roll-off coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'RB': {'description': 'Zero - bias(maximum) base resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'RC': {'description': 'Collector ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'TF': {'description': 'Ideal forward transit time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': ''},
        'TR': {'description': 'Ideal reverse transit time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': ''},
        'VAF': {'description': 'Forward Early voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'VJC': {'description': '', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'VJE': {'description': 'Base-emitter built-in potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'VTF': {'description': 'Transit time dependency on Vbc', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'XTB': {'description': 'Forward and reverse beta temperature coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'XTF': {'description': 'Transit time bias dependence coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'XTI': {'description': 'IS temperature effect exponent', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''}}


    def __init__(self, collector=None, base=None, emitter=None, gnd=None,*args, **kwargs):
        self.model = self.selected_part and self.selected_part.model
        self.collector = collector
        self.base = base
        self.emitter = emitter
        self.gnd = gnd

        self.circuit(*args, **kwargs)

    
    @property
    def spice_part(self):
        return Build('BJT').spice

    @property
    def part(self):
        if not self.DEBUG:
            # TODO: Search for models and footprints using low level attributes of Block
            part = Part('Transisotr_BJT', self.model, footprint=self.footprint, dest=TEMPLATE)
            part.set_pin_alias('collector', 1)
            part.set_pin_alias('base', 2)
            part.set_pin_alias('emitter', 3)

            return part
        else:
            return self.spice_part


    def circuit(self):
        self.input = Net('BJTInput')
        self.output = Net('BJTOutput')
        self.input_n = Net('BJTInputN')
        self.output_n = Net('BJTOutputN')

        self.v_ref = Net()
        self.gnd = Net()

        
        transistor = self.part(model=self.model)

        common = self.props.get('common', 'emitter')
        follow = self.props.get('follow', 'collector')

        if self[common]:
            common_line = transistor[common] & self[common] & self.gnd
        else:
            self.gnd += transistor[common]

        input_side = 'emitter' if common == 'base' else 'base'
        if self[input_side]:
            input_line = self.input & self[input_side] & transistor[input_side]
        else:
            self.input += transistor[input_side]

        v_ref_side = 'emitter' if common == 'collector' else 'collector'
        if self[v_ref_side]:
            v_ref_line = self.v_ref & self[v_ref_side] & transistor[v_ref_side]
        else:
            self.v_ref += transistor[v_ref_side]

        self.collector, self.base, self.emitter = transistor['collector', 'base', 'emitter']

        self.output += self[follow]