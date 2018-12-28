from pathlib import Path
import importlib
from settings import BLOCKS_PATH, DEBUG, parts
import matplotlib.pyplot as plt
from skidl import subcircuit, Net, Network, Part, TEMPLATE
from copy import copy

import logging
logger = logging.getLogger(__name__)

def label_prepare(text):
    last_dash = text.rfind('_')
    if last_dash > 0:
        text = text[:last_dash] + '$_{' + text[last_dash + 1:] + '}$'

    return text
    
    
class Build:
    def __init__(self, name, **kwargs):
        self.name = name
        self.mods = {}
        self.props = {}
        self.models = []

        base_file = Path(BLOCKS_PATH) / self.name / ('__init__.py')
        self.base = base_file.exists() and importlib.import_module(BLOCKS_PATH + '.' + self.name).Base        
        
        for mod, value in kwargs.items():
            module_file = Path(BLOCKS_PATH) / self.name / ('_' + mod) / (value + '.py')

            if module_file.exists():
                Module = importlib.import_module(BLOCKS_PATH + '.' + self.name + '._' + mod + '.' + value)
                self.models.append(Module.Modificator)
                self.mods[mod] = value
            else:
                self.props[mod] = value

    @property
    def block(self):
        if self.base:
            Models = self.models
            Models.append(self.base)
            Models = tuple(self.models)
        else:
            Models = (Block,)

        return type(self.name,
                    Models,
                    {
                        'name': self.name,
                        'mods': self.mods,
                        'props': self.props,
                        'DEBUG': DEBUG
                    })().create_circuit

    @property
    def element(self):
        return self.block().element


class Block:
    name = None
    mods = {}
    props = {}

    input = None
    output = None
    gnd = None

    element = None
    simulation = None

    DEBUG = False

    def __str__(self):
        body = [self.name]
        for key, value in self.mods.items():
            body.append(key + ' = ' + value)
        
        return '\n'.join(body)

    def  __series__(self, instance):
        if self.output and instance.input:
            print(self.output)
            print(instance.input)
            
            self.output += instance.input
            self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
            
            # instance.input._name = self.output._name
            
        if self.gnd and instance.gnd:
            self.gnd += instance.gnd
    
    def __parallel__(self, instance):
        self.input += instance.input
        self.output += instance.output
             
        if self.gnd and instance.gnd:
            self.gnd += instance.gnd

    def __getitem__(self, *pin_ids, **criteria):
        return self.element.__getitem__(*pin_ids, **criteria)

    def __and__(self, instance):
        # print(f'{self.title} series connect {instance.title if hasattr(instance, "title") else instance.name}')

        if issubclass(type(instance), Block):
            self.__series__(instance)

            return instance
        else:
            try:
                ntwk = instance.create_network()
            except AttributeError:
                raise Exception

            return Network(self.input, ntwk[-1])
    

    def __or__(self, instance):
        # print(f'{self.title} parallel connect {instance.title if hasattr(instance, "title") else instance.name}')
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
    
    @property
    def part(self):
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
    def footprint(self):
        params = list(self.props.keys()) + list(self.mods.keys())
        values = list(self.props.values()) + list(self.mods.values())

        if self.props.get('footprint', None):
            return self.props['footprint']

        for part in parts.get(self.name, []):
            for index, param in enumerate(params):
                if part.get(param, None) and part[param] != values[index]:
                    break
            else:
                return part['footprint']

            continue

        return None

    @property
    def clone(self):
        return copy(self)

    @subcircuit
    def create_circuit(self, **kwargs):
        Model = None
        if self.DEBUG:
            Model = self.spice_part
        else:
            Model = self.part
        
        instance = copy(self)
        element = Model(**kwargs)
        instance.element = element
        
        instance.set_pins()

        return instance

    @subcircuit
    def create_network(self):
        input = Net() 
        output = Net() 
        output += self.output
        input += self.input

        return [input, output]

    def set_pins(self):
        self.input = self.element[1]
        self.output = self.element[2]
    
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
        logger.info(self.title + ' - ' + message)

    def test(self):
        from skidl.pyspice import generate_netlist, node

        # Simulate the circuit.
        circuit = generate_netlist()  # Translate the SKiDL code into a PyCircuit Circuit object.
        from time import sleep
        sleep(3)
        self.simulation = circuit.simulator()  # Create a simulator for the Circuit object.
        self.node = node

    def test_plot(self, **kwargs):
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
