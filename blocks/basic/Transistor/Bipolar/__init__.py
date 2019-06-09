from bem import Build, Net
from bem.abstract import Physical
from skidl import Part, TEMPLATE
from skidl.Net import Net as NetType
from PySpice.Unit import u_Ohm, u_uF, u_H, u_kHz

class Base(Physical()):
    """**Bipolar Transistor**
    
    When designing or looking at a transistor circuit there are **three different circuit configurations** that can be used.

    The three different transistor circuit configurations are: common emitter, common base and common collector (emitter follower), these three circuit configurations have different characteristics and one type will be chosen for a circuit dependent upon what is required.

    _|**COMMON BASE**|**COMMON COLLECTOR**|**COMMON EMITTER**
    -----|-----|-----|-----
    Voltage gain|High|Low|Medium
    Current ga)in|Low|High|Medium
    Power gain|Low|Medium|High
    Phase shift|0°|0°|180°
    Input resistance|Low|High|Medium
    Output resistance|High|Low|Medium

    * [Transistor Configurations: circuit configurations](https://www.electronics-notes.com/articles/analogue_circuits/transistor/transistor-circuit-configurations.php)
    """

    pins = {
        'v_ref': True,
        'input': True,
        'input_n': True,
        'output': True,
        'output_n': True,
        'gnd': True
    }
    
    emitter = None
    base = None
    collector = None

    props = {
        'type': ['npn', 'pnp'],
        'common': ['emitter', 'base', 'collector'],
        'follow': ['emitter', 'base', 'collector']
    }

    spice_params = {
        'BF': { 'title': 'β_f', 'description': 'Ideal maximum forward beta', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'BR': { 'description': 'Ideal maximum reverse beta', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'CJC': { 'description': 'Base-collector zero-bias p-n capacitance',
                'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': '' },
        'CJE': { 'description': 'Base-emitter zero-bias p-n capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': '' },
        'XCJC': { 'description': 'Internal base fraction of base-collector depletion capacitance', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'EG': { 'description': 'Bandgap voltage (barrier height)', 'unit': { 'suffix': 'eV', 'name': 'eV' }, 'value': '' },
        'FC': { 'description': 'Forward-bias depletion capacitor coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'IKF': { 'description': 'Corner for forward-beta high-current roll-off',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'IKR': { 'description': 'Corner for reverse-beta high-current roll-off',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'IS': { 'description': 'Transport saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'ISC': { 'description': 'Base-collector leakage saturation current',
                'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'ISE': { 'description': 'Base-emitter leakage saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'ITF': { 'description': 'Transit time dependency on Ic', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'IRB': { 'description': 'base current, where base resistance falls half-way to RBM. Use zero to indicate an infinite value.', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': '' },
        'MJC': { 'description': 'Base-collector p-n grading factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'MJE': { 'description': 'Base-emitter p-n grading factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'FC': { 'description': 'Coefficient for forward bias depletion capacitance formula for DCAP=1', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'NF': { 'description': 'Forward mode ideality factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'NR': { 'description': 'Reverse mode ideality factor', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'NC': { 'description': 'Base-collector leakage emission coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'NE': { 'description': 'Base-emitter leakage emission coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'NK': { 'description': 'High-current roll-off coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'RB': { 'description': 'Zero-bias (maximum) base resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': '' },
        'RBM': { 'description': 'Minimum high current base resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': '' },
        'RE': { 'description': 'Emitter ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': '' },
        'RC': { 'description': 'Collector ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': '' },
        'PTF': { 'description': 'grequency multiplier to determine excess phase', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'TF': { 'description': 'Ideal forward transit time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': '' },
        'TR': { 'description': 'Ideal reverse transit time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': '' },
        'VAF': { 'description': 'Forward Early voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': '' },
        'VAR': { 'description': 'Reverse mode Early voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': '' },
        'VJC': { 'description': 'Base-collecotr built-in potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': '' },
        'VJE': { 'description': 'Base-emitter built-in potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': '' },
        'VTF': { 'description': 'Transit time dependency on Vbc', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': '' },
        'XTB': { 'description': 'Forward and reverse beta temperature coefficient',
                'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'XTF': { 'description': 'Transit time bias dependence coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' },
        'XTI': { 'description': 'IS temperature effect exponent', 'unit': { 'suffix': '', 'name': 'number' }, 'value': '' }
    }

    def willMount(self, collector=None, base=None, emitter=None):
        pass

    def part_spice(self, *args, **kwargs):
        return Build('BJT').spice(*args, **kwargs)

    def part_template(self):
        # TODO: Search for models and footprints using low level attributes of Block
        library = 'Transistor_BJT'

        model = self.selected_part.scheme
        if model:
            pack = model.split(':')
            if len(pack) == 2:
                library = pack[0]
                model = pack[1]
        else:
            model = self.model

        part = Part(library, model, footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('collector', 1)
        part.set_pin_alias('base', 2)
        part.set_pin_alias('emitter', 3)

        return part

    def circuit(self):
        transistor = self.element = self.part(model=self.model)

        common = self.props.get('common', 'emitter') 
        follow = self.props.get('follow', 'collector')

        common_end = self.gnd
        if not common:
            common_end = Net('NC')
        elif type(common) == NetType:
            common_end = common

        if common and self[common]:
            common_line = transistor[common] & self[common] & common_end
        elif common and common:
            common_end += transistor[common]

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