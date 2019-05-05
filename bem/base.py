import inspect
import logging
import os
from pathlib import Path

from PySpice.Unit import FrequencyValue, PeriodValue, u_V, u_ms, u_Ohm, u_A, u_W, u_S
from PySpice.Unit.Unit import UnitValue
from skidl import TEMPLATE, Net, Network, Part, subcircuit
from skidl.Net import Net as NetType
from skidl.NetPinList import NetPinList

from .util import u, is_tolerated, label_prepare
from settings import BLOCKS_PATH, params_tolerance

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

logger = logging.getLogger(__name__)

class Block:
    name = ''
    mods = {}
    props = {}

    pins = {
        'input': True,
        'output': True,
        'vref': True,
        'gnd': ('Ground', ['output_n', 'input_n'])
    }

    input = None
    output = None

    input_n = None
    output_n = None

    v_ref = None
    gnd = None

    V = 10 @ u_V
    Power = 0 @ u_W
    Load = 1000 @ u_Ohm  # [0 @ u_Ohm, 0 @ u_A, 0 @ u_W]

    element = None
    ref = ''
    files = []

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and 'value' not in kwargs.keys():
            kwargs['value'] = args[0]
            args = args[1:]

        is_ciruit_building = kwargs.get('circuit', True)
        if kwargs.get('circuit', None) != None:
            del kwargs['circuit']

        for prop in kwargs.keys():
            if hasattr(self, prop):
                setattr(self, prop, kwargs[prop])

        self.set_pins()

        self.load(self.V)
        
        self.mount(*args, **kwargs)

        if self.Power and not hasattr(self, 'P'):
            self.consumption(self.V)

        if is_ciruit_building:
            self.circuit()

    def mount(self, *args, **kwargs):
        classes = list(inspect.getmro(self.__class__))
        classes.reverse()
        for cls in classes:
            if hasattr(cls, 'willMount'):
                mount_args_keys = inspect.getargspec(cls.willMount).args
                mount_args = {key: value for key, value in kwargs.items() if key in mount_args_keys}
        
                cls.willMount(self, *args, **mount_args)

    def willMount(self, V=None, Load=None):
        """
            V -- Volts across its input terminal and gnd
            V_out -- Volts across its output terminal and gnd
            G -- Conductance `G = 1 / Z`
            Z -- Impedance of block
            P -- The power dissipated by block
            I -- The current through a block
            I_load -- Connected load presented in Amperes
            R_load -- Connected load presented in Ohms
            P_load -- Connected load presented in Watts
        """
        pass

    # Title and Description
    # def __instance__name__(self):
    #     return [k for k,v in globals().items() if v is self]
    @property
    def SIMULATION(self):
        return builtins.SIMULATION

    def __str__(self):
        body = [self.name]
        for key, value in self.mods.items():
            body.append(key + ' = ' + str(value))
        
        return '\n'.join(body)

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
        def is_proper_cls(cls):
            if cls == object:
                return False

            if hasattr(cls, 'willMount') and cls.willMount.__doc__:
                return True
        
            if hasattr(cls, 'circuit') and cls.circuit.__doc__:
                return True

            return False
            
        def extract_doc(cls):
            doc = ''

            mount = hasattr(cls, 'willMount') and cls.willMount.__doc__
            if mount:
                doc += mount

            circuit = hasattr(cls, 'circuit') and cls.circuit.__doc__
            if circuit:
                doc += circuit

            return doc

        params = {}

        docs = [extract_doc(cls) for cls in inspect.getmro(self) if is_proper_cls(cls) ]
        docs.reverse()

        for doc in docs:
            terms = [line.strip().split(' -- ') for line in doc.split('\n') if len(line.strip())]
            for term, description in terms:
                params[term.strip()] = description.strip()
        
        return params


    # Link Routines
    def __getitem__(self, *pin_ids, **criteria):
        if len(pin_ids) == 1 and hasattr(self, str(pin_ids[0])):
            return getattr(self, pin_ids[0])

        return self.element.__getitem__(*pin_ids, **criteria)

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

    def __and__(self, instance):
        if issubclass(type(instance), Block):
            # print(f'{self.title} series connect {instance.title if hasattr(instance, "title") else instance.name}')
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
        # print(f'{self.title} parallel connect {instance.title if hasattr(instance, "title") else instance.name}')
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
            if hasattr(cls, 'willMount'):
                args += inspect.getargspec(cls.willMount).args
        
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


    def get_params(self):
        params_default = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))

        params = {}
        for param, default in params_default: 
            if param in inspect.getargspec(self.willMount).args:# or arguments.get(param, None):
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


    # Pins
    def get_pins(self):
        pins = {}
        for key, value in inspect.getmembers(self, lambda item: not (inspect.isroutine(item))):
            if type(value) == NetType and key not in ['__doc__', 'element', 'simulation', 'ref']:
                pins[key] = [str(pin).split(',')[0] for pin in getattr(self, key) and getattr(self, key).get_pins()]
       
        return pins
       
    def set_pins(self):
        for pin in self.pins.keys():
            pin_description = [self.pins[pin]] if type(self.pins[pin]) == bool else self.pins[pin]
            device_name = self.name.replace('.', '')
            net_name = device_name + ''.join([word.capitalize() for word in pin.split('_')])
            
            related_nets = [pin]

            if type(pin_description) in [list, tuple]: 
                for pin_data in pin_description:
                    if type(pin_data) == str:
                        net_name = device_name + pin_data

                    if type(pin_data) == list:
                        related_nets += pin_data
            else:
                net_name = device_name + pin_description 
            
            original_net = Net(net_name)
            
            # if not hasattr(self, 'model') and pin.find('output') != -1:
                # print(net_name.replace('.', ))
                # original_net.fixed_name = True

            for net in related_nets:
                setattr(self, net, original_net)


    
    # @property
    # def spice_model(self):
    #     return self.get_spice_model(self.model)
 
    # Circuit Creation
    def circuit(self, *args, **kwargs):
        element = self.part(*args, **kwargs)

        element.ref = self.ref or element.ref 
        self.element = element
        
        self.input += self.element[1]
        self.output += self.element[2]


    # Consumption and Load
    def consumption(self, V):
        self.P = None
        self.I = None
        self.Z = None

        if self.Power == 0 @ u_Ohm or V == 0:
            return

        Power = self.Power
        
        if Power.is_same_unit(1 @ u_Ohm):
            self.Z = Power
            self.I = V / self.Z
        
        if Power.is_same_unit(1 @ u_W):
            self.P = Power
            self.I = self.P / V
        else:
            if Power.is_same_unit(1 @ u_A):
                self.I = Power

            self.P = V * self.I

        if not self.Z:
            self.Z = V / self.I

        self.G = (1 / self.Z) @ u_S

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

        self.load_args = {
            'V': V_load,
            'Load': self.Load
        } 
        
    def current(self, voltage, impedance):
        return voltage / impedance

    def power(self, voltage, impedance):
        return voltage * voltage / impedance
        
    def log(self, message):
        logger.info(self.title() + ' - ' + str(message))


