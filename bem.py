import importlib
import inspect
import logging
from pathlib import Path

from PySpice.Unit import PeriodValue, u_ms, FrequencyValue
from PySpice.Unit.Unit import UnitValue
from skidl import TEMPLATE, Net, Network, Part, subcircuit
from skidl.Net import Net as NetType

from settings import BLOCKS_PATH, DEBUG, parts

logger = logging.getLogger(__name__)

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

def label_prepare(text):
    last_dash = text.rfind('_')
    if last_dash > 0:
        text = text[:last_dash] + '$_{' + text[last_dash + 1:] + '}$'

    return text
    
    
class Build:
    name = None
    base = None
    mods = {}
    props = {}
    models = {}
    files = []

    def __init__(self, name, **kwargs):
        self.name = name
        self.mods = {}
        self.props = {}
        self.models = []
        self.files = []

        base_file = Path(BLOCKS_PATH) / self.name / ('__init__.py')
        self.base = base_file.exists() and importlib.import_module(BLOCKS_PATH + '.' + self.name).Base        

        if self.base:
            self.files.append(str(base_file))

            for mod, value in kwargs.items():
                if type(value) == list:
                    self.mods[mod] = value
                else:
                    value = str(value)
                    self.mods[mod] = value.split(',')

            for mod, value in self.base.mods.items():
                if not self.mods.get(mod, None):
                    self.mods[mod] = value

            for mod, values in self.mods.items():
                if type(values) != list:
                    values = [str(values)]

                for value in values:
                    module_file = Path(BLOCKS_PATH) / self.name / ('_' + mod) / (value + '.py')
                    if module_file.exists():
                        self.files.append(str(module_file))
                        Module = importlib.import_module(BLOCKS_PATH + '.' + self.name + '._' + mod + '.' + value)
                        self.models.append(Module.Modificator)
                    
                    else:
                        self.props[mod] = value

            for key, value in self.props.items():
                del self.mods[key]

    @property
    def block(self):
        if self.base:
            Models = self.models
            Models.reverse()
            if self.base not in Models:
                Models.append(self.base)
            Models = tuple(self.models)
        else:
            Models = (Block,)

        Block = type(self.name,
                    Models,
                    {
                        'name': self.name,
                        'mods': self.mods,
                        'props': self.props,
                        'DEBUG': DEBUG,
                        'files': self.files
                    })

        return Block

    @property
    def spice(self):
        from skidl import SKIDL, SPICE, set_default_tool, SchLib
        from skidl.tools.spice import set_net_bus_prefixes
        
        
        set_default_tool(SPICE) 
        set_net_bus_prefixes('N', 'B')
        _splib = SchLib('pyspice', tool=SKIDL)
        
        for p in _splib.get_parts():
            if self.name == p.name or (hasattr(p, 'aliases') and self.name in p.aliases):
                return p

    @property
    def element(self):
        return self.block().element


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

    def  __series__(self, instance):
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

    def connect_power_bus(self, instance):
        if self.gnd and instance.gnd:
            self.gnd += instance.gnd
        
        if self.v_ref and instance.v_ref:
            self.v_ref += instance.v_ref

    def __getitem__(self, *pin_ids, **criteria):
        return self.element.__getitem__(*pin_ids, **criteria)

    def __and__(self, instance):
        print(f'{self.title} series connect {instance.title if hasattr(instance, "title") else instance.name}')

        if issubclass(type(instance), Block):
            self.__series__(instance)

            return instance
        else:
            try:
                ntwk = instance.create_network()
            except AttributeError:
                raise Exception

            return Network(self.input, ntwk[-1])
    
    # def __rand__(self, instance):
    #     return instance & self

    def __or__(self, instance):
        print(f'{self.title} parallel connect {instance.title if hasattr(instance, "title") else instance.name}')
        if issubclass(type(instance), Block):
            self.__parallel__(instance)

            return instance
        else:
            try:
                ntwk = instance.create_network()
            except AttributeError:
                raise Exception

            self.input += ntwk[0]
            self.output += ntwk[-1]

            return self
    
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
    def available_parts(self):
        """Available parts in stock 
            from settings.py variable `parts`
            filtered by Block modifications and properties.
        
        Returns:
            list -- of parts with available values
        """

        params = list(self.props.keys()) + list(self.mods.keys())
        values = list(self.props.values()) + list(self.mods.values())

        available = []
        
        for part in parts.get(self.name, []):
            for index, param in enumerate(params):
                if part.get(param, None):
                    if type(values[index]) == list and part[param] in values[index]:
                        continue
                    if part[param] == type(part[param])(values[index]):
                        continue

                    break
                    

                print(param, part[param], values[index])
            else:
                available.append(part)

            continue

        return available


    @property
    def footprint(self):
        if self.props.get('footprint', None):
            return self.props['footprint']

        block_parts = self.available_parts
        if len(block_parts):
            return block_parts[0]['footprint']

        return None

    def circuit(self, *args, **kwargs):
        Model = None
        if self.DEBUG:
            Model = self.spice_part
        else:
            Model = self.part

        if not Model:
            return

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
        from skidl.pyspice import node

        # Simulate the circuit.
        circuit = builtins.default_circuit.generate_netlist(libs=libs)  # Translate the SKiDL code into a PyCircuit Circuit object.
        print(circuit)
        self.simulation = circuit.simulator()  # Create a simulator for the Circuit object.
        self.node = node

    def test_sources(self):
        gnd = ['gnd']
        if len(self.test_load()) == 0:
            gnd.append('output')

        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 120,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': gnd
                }
        }]
    
    def test_load(self):
        return [{
                'name': 'RLC',
                'mods': {
                    'series': ['R']
                },
                'args': {
                    'R_series': {
                        'value': 1000,
                        'unit': {
                            'name': 'ohm',
                            'suffix': 'Ω'
                        }
                    }
                },
                'pins': {
                    'input': ['output'],
                    'output': ['gnd']
                }
        }]

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

    def test_pins(self, libs=[], step_time=0.01 @ u_ms, end_time=200 @ u_ms):
        self.test(libs)

        waveforms = self.simulation.transient(step_time=step_time, end_time=end_time)  # Run a transient simulation from 0 to 10 msec.
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

        # input = waveforms[self.node(self.input)]  # Voltage on the positive terminal of the pulsed voltage source.
        # output = waveforms[self.node(self.output)]  # Voltage on the capacitor.
        current = waveforms['VS']
        
        data = []
        for index, time in enumerate(time):
            entry = {
                'time': time.value * time.scale,
                 'I_out': current[index].scale*current[index].value,
            }
            
            for key in chart_data.keys():
                entry[key] = chart_data[key][index].scale * chart_data[key][index].value 

            data.append(entry)

        return data

    def test_voltage(self, step_time=0.5 @ u_ms, end_time=200 @ u_ms):
        self.test()

        waveforms = self.simulation.transient(step_time=step_time, end_time=end_time)  # Run a transient simulation from 0 to 10 msec.

        # Get the simulation data.
        time = waveforms.time                # Time values for each point on the waveforms.
        input = waveforms[self.node(self.input)]  # Voltage on the positive terminal of the pulsed voltage source.
        
        output = waveforms[self.node(self.output)]  # Voltage on the capacitor.

        self.test_plot(Time_ms=time.as_ndarray() * 1000, V_input=input.as_ndarray(), V_output=output.as_ndarray(),
                       plots=[('Time_ms', 'V_input'), ('Time_ms', 'V_output')],
                       table=False)
