import inspect
import logging
import os
from pathlib import Path

from PySpice.Unit import FrequencyValue, PeriodValue, u_ms
from PySpice.Unit.Unit import UnitValue
from skidl import TEMPLATE, Net, Network, Part, subcircuit
from skidl.Net import Net as NetType
from skidl.NetPinList import NetPinList

from .model import Part as PartModel
from .model import Param, Mod, Prop
from .util import u, is_tolerated, label_prepare
from settings import BLOCKS_PATH, params_tolerance, parts

logger = logging.getLogger(__name__)
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

class Block:
    name = ''
    mods = {}
    props = {}

    input = None
    output = None

    input_n = None
    output_n = None

    v_ref = None
    gnd = None

    element = None
    ref = ''
    files = []

    def __init__(self, circuit=True, *args, **kwargs):
        for prop in kwargs.keys():
            if hasattr(self, prop):
                setattr(self, prop, kwargs[prop])
       
        if circuit:
            self.circuit()


    # Title and Description
    @property
    def __instance__name__(self):
        return [k for k,v in globals().items() if v is self]

    def __str__(self):
        body = [self.name]
        for key, value in self.mods.items():
            body.append(key + ' = ' + str(value))
        
        return '\n'.join(body)

    @property
    def title(self):
        input = self.input
        output = self.output
        
        input_name = f'{input.part.name}_{input.name}' if hasattr(input, 'part') else f'{input.name}' if input else "NC"
        output_name = f'{output.part.name}_{output.name}' if hasattr(output, 'part') else f'{output.name}' if output else "NC"
        
        input_name = input_name.replace(self.name, '')
        output_name = output_name.replace(self.name, '')

        return label_prepare(input_name) + ' ⟶ ' + self.name + ' ⟶ ' + label_prepare(output_name)

    def get_description(self):
        description = []
        for doc in [cls.__doc__ for cls in inspect.getmro(self) if cls.__doc__ and cls != object]:
            doc = '\n'.join([line.strip() for line in doc.split('\n')])
            description.append(doc)
        
        return description


    # Link Routines
    def __series__(self, instance):
        if self.output and instance.input:
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            self.output += instance.input
        
        if self.output_n and instance.input_n:
            self.output_n += instance.input_n
        
        self.connect_power_bus(instance)

    def __parallel__(self, instance):
        self.input += instance.input
        self.input_n += instance.input_n

        self.output += instance.output
        self.output_n += instance.output_n

        self.connect_power_bus(instance)

    def __getitem__(self, *pin_ids, **criteria):
        if len(pin_ids) == 1 and hasattr(self, str(pin_ids[0])):
            return getattr(self, pin_ids[0])

        return self.element.__getitem__(*pin_ids, **criteria)

    def __and__(self, instance):
        if issubclass(type(instance), Block):
            print(f'{self.title} series connect {instance.title if hasattr(instance, "title") else instance.name}')
            self.__series__(instance)

            return instance
        elif type(instance) == NetPinList:
            return self.__and__(instance[0])
        else:
            try:
                ntwk = instance.create_network()
            except AttributeError:
                raise Exception
            
            self.output += ntwk[0]

            return ntwk[-1]
            # return Network(self.output, ntwk[-1])

        raise Exception

    # def __rand__(self, instance):
    #     print('RAND')
    #     return instance & self

    def __or__(self, instance):
        print(f'{self.title} parallel connect {instance.title if hasattr(instance, "title") else instance.name}')
        if issubclass(type(instance), Block):
            self.__parallel__(instance)

            return NetPinList([self, instance])
        elif type(instance) == NetPinList:
            return self.__and__(instance[0])
        else:
            try:
                ntwk = instance.create_network()
            except AttributeError:
                raise Exception

            self.input += ntwk[0]
            self.output += ntwk[-1]

            return self

    def connect_power_bus(self, instance):
        if self.gnd and instance.gnd:
            self.gnd += instance.gnd
        
        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref
    

    # Virtual Part
    def get_arguments(self, Instance=None):
        arguments = {}
        args = []
        classes = list(inspect.getmro(self))
        classes.reverse()
        for cls in classes:
            args += inspect.getargspec(cls.__init__).args
        
        for arg in args:
            if arg in ['self', 'circuit']:
                continue

            default = getattr(Instance or self, arg)
            if type(default) in [UnitValue, PeriodValue, FrequencyValue]:
                arguments[arg] = {
                    'value': default.value * default.scale,
                    'unit': {
                        'name': default.unit.unit_name,
                        'suffix': default.unit.unit_suffix
                    }
                }
            elif type(default) in [int, float]:
                arguments[arg] = {
                    'value': default,
                    'unit': {
                        'name': 'number'
                    }
                }
            elif type(default) == str:
                arguments[arg] = {
                    'value': default,
                    'unit': {
                        'name': 'string'
                    }
                }
            # elif type(default) == list and len(default) > 0:
            #     arguments[arg] = {
            #         'value': default.value * default.scale,
            #         'unit': {
            #             'name': default.unit.unit_name,
            #             'suffix': default.unit.unit_suffix
            #         }
            #     }
            elif type(default) == type(None):
                arguments[arg] = {
                    'unit': {
                        'name': 'network'
                    }
                }

        return arguments
    
    def get_params(self):
        params = {}
        for param, default in inspect.getmembers(self, lambda a:not(inspect.isroutine(a))):
            if param in inspect.getargspec(self.__init__).args:
                continue
            
            if type(default) in [UnitValue, PeriodValue, FrequencyValue]:
                default = default.canonise()
                params[param] = {
                    'value': default.value,
                    'unit': {
                        'name': default.unit.unit_name,
                        'suffix': default.prefixed_unit.str() #unit.unit_suffix
                    }
                }
            elif type(default) in [int, float]:
                params[param] = {
                    'value': default,
                    'unit': {
                        'name': 'number'
                    }
                }
            elif type(default) == str and param not in ['title', 'name', '__module__']:
                params[param] = {
                    'value': default,
                    'unit': {
                        'name': 'string'
                    }
                }
        
        return params

    def get_pins(self):
        pins = {}
        for key, value in inspect.getmembers(self, lambda item: not (inspect.isroutine(item))):
            if type(value) == NetType and key not in ['__doc__', 'element', 'simulation', 'ref']:
                pins[key] = [str(pin) for pin in getattr(self, key) and getattr(self, key).get_pins()]

        return pins
        
    @property
    def part(self):
        if self.DEBUG:
            return None

        part = None

        if self.props.get('part', None) or self.name.find(':') != -1:
            part = self.props.get('part', None) or self.name

            library, device = part.split(':')
            part = Part(library, device, footprint=self.footprint, dest=TEMPLATE)

            if len(part.pins) == 2:
                part.set_pin_alias('p', 1)
                part.set_pin_alias('n', 2)
        
        return part

    @property
    def spice_part(self):
        return self.part

    @property
    def spice_model(self):
        return self.get_spice_model(self.model)
    

    # Physical Part
    @property
    def available_parts(self):
        """Available parts in stock 
            from Part model
            filtered by Block modifications and params and spice model.
        
        Returns:
            list -- of parts with available values
        """


        params = list(self.props.keys()) + list(self.mods.keys())
        values = list(self.props.values()) + list(self.mods.values())

        available = []

        parts = PartModel.select().where(PartModel.block == self.name)
        if hasattr(self, 'model') and self.model:
            parts = parts.where(PartModel.model.contains(self.model))
        
        for part in parts:
            for index, param in enumerate(params):
                if param == 'value':
                    continue

                is_proper = True
                value = values[index]
                
                part_params = part.params.where(Param.name == param)
                if part_params.count():
                    for part_param in part_params:
                        if is_tolerated(value, part_param.value):
                            break
                    else:
                        is_proper = False
                
                part_mods = part.mods.where(Mod.name == param)
                if part_mods.count():
                    for part_mod in part_mods:
                        if is_tolerated(value, part_mod.value):
                            break
                    else:
                        is_proper = False
                
                part_props = part.props.where(Prop.name == param)
                if part_props.count():
                    for part_prop in part_props:
                        if is_tolerated(value, part_prop.value):
                            break
                    else:
                        is_proper = False
                
                spice_param = part.spice_params.get(param, None)
                if spice_param:
                    if is_tolerated(value, spice_param):
                        continue

                    is_proper = False 
                             
                if is_proper:
                    continue

                break
            else:
                available.append(part)

        return available
            
    @property
    def selected_part(self):
        available = list(self.available_parts)

        return available[0] if len(available) > 0 else None

    @property
    def footprint(self):
        if self.props.get('footprint', None):
            return self.props['footprint']

        part = self.selected_part
        if part:
            return part.footprint.replace('=', ':')

        return None


    # Circuit Creation
    def circuit(self, *args, **kwargs):
        Model = None
        if self.DEBUG:
            Model = self.spice_part
        else:
            Model = self.part

        if not Model:
            return

        if hasattr(self, 'model'):
            kwargs['model'] = self.model

        element = Model(*args, **kwargs)
        element.ref = self.ref or element.ref 
        self.element = element
        
        self.set_pins()

    def create_network(self):
        return [self.input, self.output]

    def set_pins(self):
        self.input = Net('Input') 
        self.output = Net('Output')
        self.input += self.element[1]
        self.output += self.element[2]
        
        # self.gnd == Net('0')
        self.v_ref = Net()
        self.input_n = self.output_n = self.gnd = Net()



    def log(self, message):
        logger.info(self.title + ' - ' + str(message))


    # Properties
    def power(self):
        return None

