from bem import Build, Net
from bem.abstract import Physical, Network
from skidl import Part, TEMPLATE
from skidl.Net import Net as NetType
from PySpice.Unit import u_Ohm, u_uF, u_H, u_kHz

class Base(Physical(). Network(port='two')):
    """**Op Amp**
    
    """

     spice_params = {} 

    def willMount(self, drain=None, gate=None, source=None, gnd=None):
        pass
        # super().willMount(model=model)
    
    def part_spice(self, *args, **kwargs):
        part = Build(self.selected_part.scheme or self.model + ':' + self.model).spice

        part.set_pin_alias('drain', 1)
        part.set_pin_alias('gate', 2)
        part.set_pin_alias('source', 3)

        return part(*args, **kwargs)

    def part_template(self):
        # TODO: Search for models and footprints using low level attributes of Block
        part = Part('Transistor_FET', self.selected_part.scheme or self.model, footprint=self.footprint, dest=TEMPLATE)
        part.set_pin_alias('drain', 1)
        part.set_pin_alias('gate', 2)
        part.set_pin_alias('source', 3)

        return part

    def circuit(self):
        self.input = Net('FETInput')
        self.output = Net('FETOutput')
        self.input_n = Net('FETInputN')
        self.output_n = Net('FETOutputN')

        self.v_ref = Net()
        self.gnd = Net()
        transistor = self.element = self.part(model=self.model)

        common = self.props.get('common', 'source')
        follow = self.props.get('follow', 'drain')

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