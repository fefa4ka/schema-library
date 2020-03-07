from bem import Build 
from bem.abstract import Physical, Network
from skidl import Part, Net, TEMPLATE
from skidl.Net import Net as NetType
from PySpice.Unit import u_Ohm, u_uF, u_H, u_kHz

class Base(Physical(), Network(port='two')):
    """**Field Transistor**

    """

    pins = {
        'v_ref': True,
        'input': True,
        'input_n': True,
        'output': True,
        'output_n': True,
        'gnd': True
    }

    source = None
    gate = None
    drain = None

    props = {
        'type': ['mosfet', 'jfet'],
        'channel': ['n', 'p'],
        'common': ['source', 'gate', 'drain'],
        'follow': ['source', 'gate', 'drain']
    }

    spice_params = {
        'L': { 'description': 'the gate length', 'unit': { 'suffix': 'm', 'name': 'metre' }, 'value': ''},
        'W': { 'description': 'the gate width', 'unit': { 'suffix': 'm', 'name': 'metre' }, 'value': ''},
        'AD': { 'description': 'the drain area', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'AS': { 'description': 'the source area', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'LD': { 'description': 'lateral diffusion (length)', 'unit': { 'suffix': 'm', 'name': 'metre' }, 'value': ''},
        'RD': { 'description': 'drain ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'RG': {'description': 'gate ohmic resistance', 'unit': {'suffix': 'Ω', 'name': 'ohm'}, 'value': ''},
        'RS': { 'description': 'source ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'RB': { 'description': 'bulk ohmic resistance', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'IS': { 'description': 'bulk p-n saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'CBD': { 'description': 'bulk-drain zero-bias p-n capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'CGSO': {'description': 'gate-source overlap capacitance/channel width', 'unit': {'suffix': 'm', 'name': 'metre'}, 'value': ''},
        'CGDO': {'description': 'gate-drain overlap capacitance/channel width', 'unit': {'suffix': 'm', 'name': 'metre'}, 'value': ''},
        'XJ': { 'description': 'metallurgical junction depth', 'unit': { 'suffix': 'm', 'name': 'metre' }, 'value': ''},
        'WD': { 'description': 'lateral diffusion (width)', 'unit': { 'suffix': 'm', 'name': 'metre' }, 'value': ''},
        'JS': { 'description': 'bulk p-n saturation current/area', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'CBS': { 'description': 'bulk-source zero-bias p-n capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'VTO': { 'description': 'Threshold voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'KP': { 'description': 'Transconductance parameter', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'GAMMA': { 'description': 'Bulk threshold parameter', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'PHI': { 'description': 'Surface potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'LAMBDA': { 'description': 'Channel length modulation parameter', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'MJ': { 'description': 'Bulk junction grading coefficient(dimensionless)', 'unit': { 'suffix': '', 'name': '' }, 'value': ''},
        'PB': { 'description': 'Built-in potential for the bulk junction', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''}
    }

    def willMount(self, drain=None, gate=None, source=None, gnd=None):
        pass
        # super().willMount(model=model)

    def part_spice(self, *args, **kwargs):
        is_spice_subciruit = 'SUBCKT' in self.selected_part.spice.upper()
        part = None

        if is_spice_subciruit:
            part = Build((self.selected_part.symbol or self.model) + ':' + self.model).spice
        else:
            part = Build('M').spice

        part.set_pin_alias('drain', 1)
        part.set_pin_alias('gate', 2)
        part.set_pin_alias('source', 3)

        return part(*args, **kwargs)

    def part_template(self):
        # TODO: Search for models and footprints using low level attributes of Block
        part = super().part_template()

        part.set_pin_alias('drain', 2)
        part.set_pin_alias('gate', 1)
        part.set_pin_alias('source', 3)

        return part

    def circuit(self):
        transistor = self.element = self.part(model=self.model)

        common = self.props.get('common', 'source')
        follow = self.props.get('follow', 'drain')

        if not self.gnd:
            self.gnd = Net('FieldGnd')

        common_end = self.gnd
        if not common:
            common_end = Net('NC')
        elif type(common) == NetType:
            common_end = common

        if common and self[common]:
            common_line = transistor[common] & self[common] & common_end
        elif common and common:
            common_end += transistor[common]

        input_side = 'source' if common == 'gate' else 'gate'
        if self[input_side]:
            input_line = self.input & self[input_side] & transistor[input_side]
        else:
            self.input += transistor[input_side]

        v_ref_side = 'source' if common == 'drain' else 'drain'
        if self[v_ref_side]:
            v_ref_line = self.v_ref & self[v_ref_side] & transistor[v_ref_side]
        else:
            self.v_ref += transistor[v_ref_side]

        self.drain, self.gate, self.source = transistor['drain', 'gate', 'source']

        self.output += self[follow]
