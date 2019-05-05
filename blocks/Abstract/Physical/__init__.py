from bem import Block, Stockman

class Base(Block):
    model = ''

    template = None

    def willMount(self, model=None):
        self.selected_part = self.select_part()
        
        if self.selected_part.model != model:
            self.model = self.selected_part.model

        if self.selected_part:
            self.props['footprint'] = self.selected_part.footprint.replace('=', ':')

        if not self.SIMULATION:
            self.template = self.part_template()

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
        model = self.props.get('model', None)

        if model:
            for part in available:
                if part.model == model:
                    return part
        
        part = available[0] if len(available) > 0 else None
        
        return part

    # Physical or Spice Part
    def part_template(self):
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

        return self.template(*args, **kwargs)

    def part_spice(self, *args, **kwargs):
        return None

    @property
    def footprint(self):
        return self.props.get('footprint', None)
    

