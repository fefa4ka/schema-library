import inspect
import logging
import os
from pathlib import Path

from PySpice.Unit import FrequencyValue, PeriodValue, u_ms, u_Ohm, u_A, u_W
from PySpice.Unit.Unit import UnitValue
from skidl import TEMPLATE, Net, Network, Part, subcircuit
from skidl.Net import Net as NetType
from skidl.NetPinList import NetPinList

from .stockman import Stockman
from .util import u, is_tolerated, label_prepare
from settings import BLOCKS_PATH, params_tolerance

logger = logging.getLogger(__name__)

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

    Load = 1000 @ u_Ohm  # [0 @ u_Ohm, 0 @ u_A, 0 @ u_W]
    R_load = 0 @ u_Ohm
    I_load = 0 @ u_A
    P_load = 0 @ u_W

    element = None
    ref = ''
    files = []

    def __init__(self, circuit=True, *args, **kwargs):
        """
            V_in -- Volts across its input terminal and gnd
            V_out -- Volts across its output terminal and gnd
            P -- The power dissipated 
            I -- The current through a device
            I_load -- Connected load presented in Amperes
            R_load -- Connected load presented in Ohms
            P_load -- Connected load presented in Watts
        """
   

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

    def get_params_description(self):
        params = {}
        docs = [cls.__init__.__doc__ for cls in inspect.getmro(self) if cls.__init__.__doc__ and cls != object]
        docs.reverse()
        for doc in docs:
            terms = [line.strip().split(' -- ') for line in doc.split('\n') if len(line.strip())]
            for term, description in terms:
                params[term.strip()] = description.strip()
        
        return params

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

    def create_network(self):
        return [self.input, self.output]

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
            elif arg == 'Load' and type(default) == list and len(default) > 0:
                default = default[0]
                # arguments[arg] = {
                #     'value': default.value * default.scale
                #     'unit': {
                #         'name': default.unit.unit_name,
                #         'suffix': default.unit.unit_suffix
                #     }
                # }
                arguments[arg] = {
                    'value': default.value * default.scale,
                    'unit': {
                        'name': default.unit.unit_name,
                        'suffix': default.unit.unit_suffix
                    }
                }
            elif type(default) == type(None):
                arguments[arg] = {
                    'unit': {
                        'name': 'network'
                    }
                }

        return arguments
    
    def get_params(self):
        # arguments = self.get_arguments()
        params = {}
        for param, default in inspect.getmembers(self, lambda a:not(inspect.isroutine(a))):
            if param in inspect.getargspec(self.__init__).args:# or arguments.get(param, None):
                continue
            
            if type(default) in [UnitValue, PeriodValue, FrequencyValue]:
                default = default.canonise()
                params[param] = {
                    'value': round(default.value, 1),
                    'unit': {
                        'name': default.unit.unit_name,
                        'suffix': default.prefixed_unit.str() #unit.unit_suffix
                    }
                }
            elif type(default) in [int, float]:
                params[param] = {
                    'value': default if type(default) == int else round(default, 3),
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

    def parse_args(self, args):
        arguments = self.get_arguments(self)
        props = {}
        for attr in arguments:
            props[attr] = getattr(self, attr)
            if type(props[attr]) == list:
                props[attr] = props[attr][0]
            arg = args.get(attr, None)
            if arg: 
                if type(arg) == dict:
                    arg = arg['value']
                
                if type(props[attr]) in [int, float]:
                    props[attr] = float(arg)
                elif type(props[attr]) == str:
                    props[attr] = arg
                elif type(props[attr]) == list:
                    props[attr] = props[attr][0]
                else:
                    props[attr]._value = float(arg)
        
        return props

    def get_pins(self):
        pins = {}
        for key, value in inspect.getmembers(self, lambda item: not (inspect.isroutine(item))):
            if type(value) == NetType and key not in ['__doc__', 'element', 'simulation', 'ref']:
                pins[key] = [str(pin).split(',')[0] for pin in getattr(self, key) and getattr(self, key).get_pins()]
       
        return pins
       
    def set_pins(self):
        self.input = Net('Input') 
        self.output = Net('Output')
        self.input += self.element[1]
        self.output += self.element[2]
        
        # self.gnd == Net('0')
        self.v_ref = Net()
        self.input_n = self.output_n = self.gnd = Net()
 


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
        parts = Stockman(self).suitable_parts()

        return parts
      
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



    def log(self, message):
        logger.info(self.title + ' - ' + str(message))


    # Properties
    def load(self, V_load):
        Load = self.Load
        
        if Load.is_same_unit(1 @ u_Ohm):
            self.R_load = Load
            self.I_load = V_load / self.R_load
        
        if Load.is_same_unit(1 @ u_W):
            self.P_load = Load
            self.I_load = self.P_load / V_load
        else:
            if Load.is_same_unit(1 @ u_A):
                self.I_load = Load

            self.P_load = V_load * self.I_load

        if not self.R_load:
            self.R_load = V_load / self.I_load

    def power(self):
        return None

