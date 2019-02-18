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

from settings import BLOCKS_PATH, params_tolerance, parts, test_sources, test_load

logger = logging.getLogger(__name__)
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)
def label_prepare(text):
    last_dash = text.rfind('_')
    if last_dash > 0:
        text = text[:last_dash] + '$_{' + text[last_dash + 1:] + '}$'

    return text

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
    simulation = None

    ref = None
    files = []
    DEBUG = False

    spice_params = {}
    

    def __init__(self, circuit=True, *args, **kwargs):
        for prop in kwargs.keys():
            if hasattr(self, prop):
                setattr(self, prop, kwargs[prop])
       
        if circuit:
            self.circuit()

    @property
    def __instance__name__(self):
        return [k for k,v in globals().items() if v is self]

    def __str__(self):
        body = [self.name]
        for key, value in self.mods.items():
            body.append(key + ' = ' + str(value))
        
        return '\n'.join(body)

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
    
    def get_description(self):
        description = []
        for doc in [cls.__doc__ for cls in inspect.getmro(self) if cls.__doc__ and cls != object]:
            doc = '\n'.join([line.strip() for line in doc.split('\n')])
            description.append(doc)
        
        return description

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
                params[param] = {
                    'value': default.value * default.scale,
                    'unit': {
                        'name': default.unit.unit_name,
                        'suffix': default.unit.unit_suffix
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
    
    # def get_spice_model(self, model):
    #     def parse_model(content):
    #         without_comments = filter(lambda line: line[0] != '*', content)
    #         replace_plus_joints = ''.join(without_comments).replace('+', ' ').replace('(', ' ').replace(')', ' ').replace(' =', '=').replace('= ', '=').upper()
    #         reduce_double_spaces = ' '.join(replace_plus_joints.split())
    #         spice_model = reduce_double_spaces.split(' ')

    #         params = {}
    #         if len(self.spice_params.keys()):
    #             for param in spice_model[3:]:
    #                 param, value = param.split('=')
    #                 params[param] = self.spice_params.get(param, {})
    #                 params[param]['value'] = float(value)

    #         return params

    #     def check_in_dir(path):
    #         if not path.exists():
    #             return None

    #         for part in path.iterdir():
    #             file_model = os.path.basename(part).split('.')[0].lower()
    #             if model.lower() == file_model:
    #                 file = open(part, 'r')
    #                 params = parse_model(file.readlines())
    #                 file.close()
                    
    #                 return params

    #         return None
                    
    #     if model:
    #         spice_lib_path = Path(BLOCKS_PATH) / self.name / ('spice')
    #         part = check_in_dir(spice_lib_path)
    #         if part:
    #             return part

    #         for mod in self.mods.keys():
    #             spice_lib_path = Path(BLOCKS_PATH) / self.name / ('_' + mod) / ('spice')
    #             part = check_in_dir(spice_lib_path)
    #             if part:
    #                 return part

    #     return None

    # def parse_spice_model(self, content):
    #     without_comments = filter(lambda line: line[0] != '*', content)
    #     replace_plus_joints = ''.join(without_comments).replace('+', ' ').replace('(', ' ').replace(')', ' ').replace(' =', '=').replace('= ', '=').upper()
    #     reduce_double_spaces = ' '.join(replace_plus_joints.split())
    #     spice_model = reduce_double_spaces.split(' ')

    #     params = {}
    #     if len(self.spice_params.keys()):
    #         for param in spice_model[3:]:
    #             param, value = param.split('=')
    #             params[param] = self.spice_params.get(param, {})
    #             params[param]['value'] = float(value)

    #     return params
        
    @property
    def available_parts(self):
        """Available parts in stock 
            # from settings.py variable `parts`
            from Part model
            filtered by Block modifications and params and spice model.
        
        Returns:
            list -- of parts with available values
        """

        def is_tollerated(a, b, tollerance=params_tolerance):
            if type(a) == list and b in a:
                return True

            if b == type(b)(a):
                return True

            try:
                b = float(b)
                a = float(a)
                diff = abs(a - b)
                if diff < a * tollerance:
                    return True
            except:
                pass
            
            return False

        params = list(self.props.keys()) + list(self.mods.keys())
        values = list(self.props.values()) + list(self.mods.values())

        available = []

        parts = PartModel.select().where(PartModel.block == self.name)
        if hasattr(self, 'model') and self.model:
            parts = parts.where(PartModel.model.contains(self.model))
        
        for part in parts:
            for index, param in enumerate(params):
                is_proper = True
                value = values[index]
                
                part_params = part.params.where(Param.name == param)
                if part_params.count():
                    for part_param in part_params:
                        if is_tollerated(value, part_param.value):
                            break
                    else:
                        is_proper = False

                part_mods = part.mods.where(Mod.name == param)
                if part_mods.count():
                    for part_mod in part_mods:
                        if is_tollerated(value, part_mod.value):
                            break
                    else:
                        is_proper = False

                part_props = part.props.where(Prop.name == param)
                if part_props.count():
                    for part_prop in part_props:
                        if is_tollerated(value, part_prop.value):
                            break
                    else:
                        is_proper = False

                spice_param = part.spice_params.get(param, None)
                if spice_param:
                    if is_tollerated(value, spice_param):
                        continue

                    is_proper = False 
                
                if is_proper:
                    continue

                break
            else:
                available.append(part)

        return available
            
        # for part in parts.get(self.name, []):
        #     if part.get('model', None):
        #         part['spice_model'] = self.get_spice_model(part['model'])

        #     for index, param in enumerate(params):
        #         if part.get(param, None):
        #             if type(values[index]) == list and part[param] in values[index]:
        #                 continue

        #             if part[param] == type(part[param])(values[index]):
        #                 continue

        #             break
                
        #         if part.get('spice_model', None) and part['spice_model'].get(param, None):
        #             value = float(values[index])
        #             part_value = float(part['spice_model'][param]['value'])
                    
        #             diff = abs(value - part_value)
        #             print(param, diff, value * params_tolerance, value, part_value)
        #             if diff < value * params_tolerance:
        #                 continue

        #             break  
        #     else:                   
        #         available.append(part)

        #     continue

        # return available

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
    
    def power(self):
        return None

    @property
    def title(self):
        input = self.input
        output = self.output
        
        input_name = f'{input.part.name}_{input.name}' if hasattr(input, 'part') else f'{input.name}' if input else "NC"
        output_name = f'{output.part.name}_{output.name}' if hasattr(output, 'part') else f'{output.name}' if output else "NC"
        
        input_name = input_name.replace(self.name, '')
        output_name = output_name.replace(self.name, '')

        return label_prepare(input_name) + ' ⟶ ' + self.name + ' ⟶ ' + label_prepare(output_name)

    def log(self, message):
        logger.info(self.title + ' - ' + str(message))

    def test(self, libs=[]):
        from skidl.tools.spice import node

        try:
            import __builtin__ as builtins
        except ImportError:
            import builtins

        libs = ['./spice/']
       
        # Simulate the circuit.
        circuit = builtins.default_circuit.generate_netlist(libs=libs)  # Translate the SKiDL code into a PyCircuit Circuit object.
        print(circuit)
        self.simulation = circuit.simulator()  # Create a simulator for the Circuit object.
        self.node = node

    def test_sources(self):
        sources = test_sources
        
        gnd = ['gnd']
        if len(self.test_load()) == 0:
            gnd.append('output')

        sources[0]['pins']['n'] = gnd

        return sources
    
    def test_load(self):
        return test_load

    def test_pins(self, current_nodes=[], libs=[], step_time=0.01 @ u_ms, end_time=200 @ u_ms):
        self.test(libs)

        waveforms = self.simulation.transient(step_time=step_time, end_time=end_time) 
        time = waveforms.time  # Time values for each point on the waveforms.
        
        pins = self.get_pins().keys()

        chart_data = {}
        for pin in pins:
            try: 
                net = getattr(self, pin)
                if net and pin != 'gnd' and net != self.gnd:
                    node = self.node(net)
                    chart_data['V_' + pin] = waveforms[node]
            except:
                pass

        current = {}
        for node in current_nodes:
            current[node] = -waveforms[node]
            
       
        data = []
        for index, time in enumerate(time):
            entry = {
                'time': time.value * time.scale
            }
            
            for key in current.keys():
                entry['I_' + key] = current[key][index].scale * current[key][index].value
                
            for key in chart_data.keys():
                entry[key] = chart_data[key][index].scale * chart_data[key][index].value 

            data.append(entry)

        return data

    def test_plot(self, **kwargs):
        import matplotlib.pyplot as plt
        args = list(kwargs.items())
        fields = [label_prepare(arg[0]) for arg in args]

        plots = []
        if kwargs.get('plots', None):
            for params in kwargs['plots']:
                plot = []
                for param in params:
                    plot.append([label_prepare(param), kwargs[param]])

                plots.append(plot)
        else:
            plot = [(fields[0], args[0][1]), (fields[1], args[1][1])]
            plots.append(plot)
        
        # Graph
        plt.title(self.title)
        xlabel = []
        ylabel = []
            
        for plot in plots:
            xlabel.append(plot[0][0])
            ylabel.append(plot[1][0])
            plt.plot(plot[0][1], plot[1][1], label=f'{plot[0][0]} - {plot[1][0]}')

        plt.xlabel(' / '.join(set(xlabel)))
        plt.ylabel(' / '.join(set(ylabel)))

        # Table        
        if kwargs.get('table', False):
            data = [[f'{value:.2f}' for value in arg[1]] for arg in args]
            plt.subplots_adjust(right=0.5)
            plt.table(cellText=list(zip(*data)), colLabels=fields, loc='right')

        plt.legend(loc='upper right')

        plt.show()

        # Example: 
        # self.test_plot(Time_ms=time.as_ndarray() * 1000, V_input=input.as_ndarray(), V_output=output.as_ndarray(),
        #                plots=[('Time_ms', 'V_input'), ('Time_ms', 'V_output')],
        #                table=False)
