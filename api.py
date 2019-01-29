import inspect
import glob
import os
from math import isnan
from flask import request
from flask_api import FlaskAPI
from PySpice.Unit.Unit import UnitValue
from skidl import Circuit
from collections import defaultdict
from bem import Build
from skidl import subcircuit, Net
from PySpice.Unit import u_V, u_ms, u_Ohm, u_s, u_A, u_Hz

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

app = FlaskAPI(__name__)

def get_part(name):
    from skidl.libs.pyspice_sklib import pyspice_lib

    sources = []
    for part in pyspice_lib.parts:
        if name == getattr(part, 'name', ''):
            return part

def get_arg_units(part, arg):
    description = getattr(part, 'description')
    part_type = 'current' if description.lower().find('current') != -1 else 'voltage'

    unit = None
    if arg.find('time') != -1 or arg.find('delay') != -1 or arg in ['pulse_width', 'period', 'duration']:
        unit = u_s
    
    if arg.find('frequency') != -1:
        unit = u_Hz
    
    if arg.find('amplitude') != -1 or arg.find('value') != -1 or arg.find('offset') != -1:
        if part_type == 'current':
            unit = u_A
        else:
            unit = u_V
    
    return unit

def get_minimum_period(sources):
    period = 0 # Default 100 ms
    min_period = None

    for source in sources:
        for arg in source['args'].keys():
            if arg.find('time') != -1 or arg in ['pulse_width', 'period', 'duration']:
                if source['args'][arg]['value']:
                    time = float(source['args'][arg]['value'])
                    if period < time:
                        period = time
                    
                    if not min_period or min_period > time:
                        min_period = time
            
            if arg.find('frequency') != -1:
                time = 1 / float(source['args'][arg]['value'])
                if period < time:
                    period = time
                
                if not min_period or min_period > time:
                    min_period = time

    return period if period / min_period <= 20 else period / 5

@app.route('/api/sources/', methods=['GET'])
def sources():
    from skidl.libs.pyspice_sklib import pyspice_lib

    sources = []
    for part in pyspice_lib.parts:
        name = getattr(part, 'name', '')
        description = getattr(part, 'description')
        pins = [p.name for p in part.pins]
        if description.lower().find('source') != -1:
            args = {}
            part_type = 'current' if description.lower().find('current') != -1 else 'voltage'

            for arg in list(part.pyspice.get('pos', [])) + list(part.pyspice.get('kw', [])):
                unit = get_arg_units(part, arg)

                if arg in pins:
                    unit = 'network'
                if unit == None:
                    unit = {
                        'name': 'number',
                        'suffix': ''
                    }
                elif unit == 'network':
                    unit = {
                        'name': 'network',
                        'suffix': ''
                    }
                else:
                    unit = {
                        'name': unit._prefixed_unit.unit.unit_name,
                        'suffix': unit._prefixed_unit.unit.unit_suffix
                    }

                args[arg] = {
                    'value': '',
                    'unit': unit
                }

            sources.append({
                'name': name,
                'description': description,
                'pins': pins,
                'args': args
            })
    
    return sources

@app.route('/api/blocks/', methods=['GET'])
def blocks():
    blocks = defaultdict()
    for block in [block.split('/')[2] for block in glob.glob('./blocks/*/__init__.py')]:
        blocks[block] = defaultdict(list)
        
        for mod_type, mod_value in [(mod.split('/')[3], mod.split('/')[4]) for mod in glob.glob('./blocks/%s/_*/*.py' % block)]:
            mod_type = mod_type[1:]
            mod_value = mod_value.replace('.py', '')
            blocks[block][mod_type].append(mod_value)


    return blocks

def get_arguments_values(Block, params):
    arguments = Block.get_arguments(Block)
    props = {}
    for attr in arguments:
        props[attr] = getattr(Block, attr)

        arg = params.get(attr, None)
        # if arg and type(arg) == dict:
        #     arg = arg['value']

        # if arg and not isnan(float(arg)):
        #     if type(props[attr]) in [int, float]:
        #         props[attr] = float(arg)
        #     else:
        #         props[attr]._value = float(arg)
        
        if arg: 
            if type(arg) == dict:
                arg = arg['value']
            
            if type(props[attr]) in [int, float]:
                props[attr] = float(arg)
            elif type(props[attr]) == str:
                props[attr] = arg
            else:
                props[attr]._value = float(arg)
    
    return props

@app.route('/api/blocks/<name>/', methods=['GET'])
def block(name):
    builtins.default_circuit.reset(init=True)
    del builtins.default_circuit
    builtins.default_circuit = Circuit()
    builtins.NC = builtins.default_circuit.NC
    gnd = Net('0')

    def build():
        params = request.args
        Block = Build(name, **params).block
        props = get_arguments_values(Block, params)
        
        Instance = Block(**props)
        
        parts = []
        nets = {}

        if Instance.input:
            for part in Instance.input.circuit.parts:
                pins = [str(pin) for pin in part.get_pins()]
                parts.append({
                    'name': part.name,
                    'description': part.description,
                    'pins': pins
                })

            for net in Instance.input.circuit.get_nets():
                pins = [str(pin) for pin in net.get_pins()]
                nets[net.name] = pins
        
        params = {
            'name': Block.name,
            'mods': Block.mods,
            'description': Block.get_description(Block),
            'args':  Block.get_arguments(Block, Instance),
            'params': Instance.get_params(),
            'pins': Instance.get_pins(),
            'files': Block.files,
            'parts': parts,
            'nets': nets,
            'sources': params.get('sources', Instance.test_sources()),
            'load': params.get('load', Instance.test_load())
        }
        
        return params

    params = build()
    return params

@app.route('/api/blocks/<name>/simulate/', methods=['POST'])
def simulate(name):
    builtins.default_circuit.reset(init=True)
    del builtins.default_circuit
    builtins.default_circuit = Circuit()
    builtins.NC = builtins.default_circuit.NC  


    # @subcircuit
    def build():
        gnd = Net('0')
        # builtins.default_circuit.reset()
        
        params = request.data
        Block = Build(name, **params['mods']).block
        props = get_arguments_values(Block, params['args'])
        
        
        # circuit = Circuit()
        
        # import time
        # time.sleep(1)
        # builtins.default_circuit = circuit
        # builtins.default_circuit.context = [('top',)]
        # builtins.default_circuit.NC = circuit.NC
        # gnd = Net('0')
        
        Instance = Block(**props)
        # signal = None
        # from skidl.libs.pyspice_sklib import pyspice_lib
    
        # # sources = []
        # for part in pyspice_lib.parts:
        #     name = getattr(part, 'name', '')
        #     if name == 'PULSEV':
        #         signal = part(ref='VS', initial_value=-8 @ u_V, pulsed_value=10 @ u_V, pulse_width=40 @ u_ms, period=80 @ u_ms)
        # signal = PULSEV(ref='VS', initial_value=-8 @ u_V, pulsed_value=10 @ u_V, pulse_width=40 @ u_ms, period=80 @ u_ms)
        # R_pr
        # e_load = Build('Resistor').block(value = 100 @ u_Ohm)
        # signal = Build('PULSEV').spice(ref='VS', initial_value=-8 @ u_V, pulsed_value=10 @ u_V, pulse_width=40 @ u_ms, period=80 @ u_ms)
        # R_load = Build('Resistor').block(value = 10000 @ u_Ohm)
        # Instance.input += signal['p']
        # gnd += signal['n']
        
        Instance.gnd += gnd
        # R_load.input += Instance.output
        # gnd += R_load.output

        sources = params['sources']
        series_sources = defaultdict(list)
        series_sources_allready = []
        
        periods = []  # frequency, time, delay, duration
        
        # Get Series Source with same input
        for source in params['sources']:
            pins = source['pins'].keys()
            hash_name = str(source['pins']['p']) + str(source['pins']['n'])
        
            for source_another_index, source_another in enumerate(params['sources']):
                is_same_connection = True
                for source_pin in pins:
                    for index, pin in enumerate(source['pins'][source_pin]):
                        if source_another['pins'][source_pin][index] != pin:
                            is_same_connection = False
                            break
                
                if is_same_connection and source_another_index not in series_sources_allready:
                    series_sources_allready.append(source_another_index)
                    series_sources[hash_name].append(source_another)

        
        for series in series_sources.keys():
            last_source = None

            for source in series_sources[series]:
                part_name = source['name'].split('_')[0]
                part = get_part(part_name)
                args = {}
                for arg in source['args'].keys():
                    if source['args'][arg]['value']:
                        args[arg] = float(source['args'][arg]['value']) @ get_arg_units(part, arg)

                signal = Build(part_name).spice(ref='VS', **args)

                if not last_source:
                    for pin in source['pins']['n']:
                        signal['n'] += getattr(Instance, pin)
                else:
                    last_source['p'] += signal['n']

                last_source = signal
            
            for pin in source['pins']['p']:
                signal['p'] += getattr(Instance, pin)

        # for source in params['sources']:
        #     part = get_part(source['name'])
        #     args = {}
        #     for arg in source['args'].keys():
        #         if source['args'][arg]['value']:
        #             args[arg] = float(source['args'][arg]['value']) @ get_arg_units(part, arg)

        #     signal = Build(source['name']).spice(ref='VS', **args)

        #     for source_pin in source['pins'].keys():
        #         for pin in source['pins'][source_pin]:
        #             signal[source_pin] += getattr(Instance, pin)

        load = params['load']
        loads = []
        for source in params['load']:
            mods = {}
            if source.get('mods', None):
                mods = source['mods']

            LoadBlock = Build(source['name'], **mods).block
            args = get_arguments_values(LoadBlock, source['args'])
            load = LoadBlock(**args)
            loads.append(load)
            
            for source_pin in source['pins'].keys():
                for pin in source['pins'][source_pin]:
                    load_pin = getattr(load, source_pin)
                    load_pin += getattr(Instance, pin)
        
        period = get_minimum_period(params['sources'])
        end_time = period * 10
        step_time = period / 50

        spice_libs = list(set([os.path.dirname(file) for file in glob.glob('./blocks/*/*/spice/*.lib')]))
        pins = Instance.test_pins(libs=spice_libs, end_time=end_time @ u_s, step_time=step_time @ u_s)

        return pins
    
    params = build()
    # builtins.default_circuit.reset()
    return params


@app.route('/api/files/', methods=['GET'])
def get_file():
    name = request.args.get('name', None)
    if name:
        file = open(name, 'r')
        return ''.join(file.readlines())
    else:
        return ''
    
@app.route('/api/files/', methods=['POST'])
def save_file():
    data = request.data
    file = open(data.get('name', ''), 'w')
    content = data.get('content', '')
    file.write(content)
    file.close()

    return { 'success': 'ok' }

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True, threaded=True)
