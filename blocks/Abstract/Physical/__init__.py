from bem import Block, Stockman
from bem.abstract import Electrical

class Base(Block):
    inherited = [Electrical]
    model = ''

    template = None

    def willMount(self, model=None):
        if not hasattr(self, 'selected_part'):
            selected_part = self.select_part()
            self.apply_part(selected_part)

    def available_parts(self):
        parts = Stockman(self).suitable_parts()

        if len(parts) == 0:
            args = self.__class__.get_arguments(self.__class__, self)
            params = self.get_params()
            values = {
                **args,
                **params
            }
            description = ', '.join([ arg + ' = ' + str(values[arg].get('value', '')) + values[arg]['unit'].get('suffix', '') for arg in values.keys()])
            
            raise LookupError("There are should be parts in stock for %s block with suitable characteristics\n%s" % (self.name, description))
            
        return parts
      
    def select_part(self):
        available = list(self.available_parts())
        model = self.model

        if model:
            for part in available:
                if part.model == model:
                    return part
        
        part = available[0] if len(available) > 0 else None
        
        return part

    def apply_part(self, part):
        self.selected_part = part
        
        if self.selected_part.model != self.model:
            self.model = self.selected_part.model

        if self.selected_part:
            self.props['footprint'] = self.selected_part.footprint.replace('=', ':')

        if not self.SIMULATION:
            self.template = self.part_template()

    # Physical or Spice Part
    def part_template(self):
        """
            self.name or self.part should contains definition with ':', for example 'Device:R' 
            or part_template method shoud redefined
        """
        part = None

        if self.props.get('part', None) or self.name.find(':') != -1:
            part = self.props.get('part', None) or self.name

            library, device = part.split(':')
            part = Part(library, device, footprint=self.footprint, dest=TEMPLATE)

            if len(part.pins) == 2:
                part.set_pin_alias('p', 1)
                part.set_pin_alias('n', 2)
    

        return part

    def part(self, *args, **kwargs):
        if self.SIMULATION:
            return self.part_spice(*args, **kwargs)

        # If IC assembly with multiply units available return free unit or new.
        return self.template(*args, **kwargs)

    @property
    def footprint(self):
        return self.props.get('footprint', None)
    

