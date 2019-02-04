import datetime
import glob
import os
from collections import defaultdict
from math import isnan

from flask import request
from flask_api import FlaskAPI

from PySpice.Unit import u_A, u_Hz, u_ms, u_Ohm, u_s, u_V
from PySpice.Unit.Unit import UnitValue
from skidl import Circuit, Net, subcircuit

from bem import Build, get_bem_blocks
from bem.model import Part, Param, Mod, Prop, Stock

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

app = FlaskAPI(__name__)


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
    blocks = get_bem_blocks()


    return blocks


def get_arguments_values(Block, params):
    arguments = Block.get_arguments(Block)
    props = {}
    for attr in arguments:
        props[attr] = getattr(Block, attr)

        arg = params.get(attr, None)
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
        
        available = [{ 'id': part.id, 'model': part.model, 'fooptrint': part.footprint } for part in Instance.available_parts]
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
            'load': params.get('load', Instance.test_load()),
            'available': available
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

    def build():
        gnd = Net('0')
        
        params = request.data
        Block = Build(name, **params['mods']).block
        props = get_arguments_values(Block, params['args'])

        Instance = Block(**props)    
        Instance.gnd += gnd

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
                # part = get_part(part_name)
                part = Build(part_name).spice
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
        simulated_data = Instance.test_pins(libs=spice_libs, end_time=end_time @ u_s, step_time=step_time @ u_s)

        return simulated_data
    
    simulated_data = build()

    return simulated_data


@app.route('/api/circuit/', methods=['POST'])
def circuit():
    builtins.default_circuit.reset(init=True)
    del builtins.default_circuit
    builtins.default_circuit = Circuit()
    builtins.NC = builtins.default_circuit.NC
    
    code = request.data.get('code', '')
    
    code_locals = {}
    exec(code, {}, code_locals)
    
    return code_locals.get('chart', [])

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


@app.route('/api/parts/', methods=['GET'])
def get_parts():
    parts = []
    block = request.args.get('block', None)
    for part in Part.select().where(Part.block == block) if block else Part.select():
        params = defaultdict(list)
        for param in part.params:
            params[param.name].append(param.value)

        parts.append({
            'id': part.id,
            'block': part.block,
            'model': part.model,
            'footprint': part.footprint,
            'mods': [mod.name + '=' + mod.value for mod in part.mods],
            'props': [prop.name + '=' + prop.value for prop in part.props],
            'params': params,
            'spice': part.spice,
            'spice_params': part.spice_params,
            'description': part.description,
            'datasheet': part.datasheet,
            'stock': [{ 'quantity': stock.quantity, 'stock': stock.place } for stock in part.stock],
        })
    
    return parts

@app.route('/api/parts/', methods=['POST'])
def add_part():
    data = request.data

    if data.get('id', None):
        __stock_delete_part(data['id'])

    part = Part(block=data['block'],
        model=data['model'],
        footprint=data['footprint'],
        datasheet=data.get('datasheet', ''),
        description=data.get('description', ''),
        spice=data.get('spice', '')
    )
    part.save()
    
    mods = []
    for mod in data.get('mods', []):
        name, value = mod.split('=')
        mod = Mod(name=name, value=value)
        mod.save()
        part.mods.add(mod)

    props = []
    for prop in data.get('props', []):
        name, value = prop.split('=')
        prop = Prop(name=name, value=value)
        prop.save()
        part.props.add(prop)

    params = []
    for name in data.get('params', {}).keys():
        values = data['params'].get(name, [])
        for value in values:
            param = Param(name=name, value=value)
            param.save()
            part.params.add(param)
        
    stock = Stock(quantity=data['quantity'], place=data['stock'])
    stock.save()
    part.stock.add(stock)

    spice_file = open('./spice/' + part.model + '.lib', 'w')
    spice_file.write('*\n' + part.spice + '\n*')
    spice_file.close()

    return  { 'part': part.id}

def __stock_delete_part(part_id):
    part = Part.get_or_none(id=part_id)
    
    if part:
        part.params.clear()
        part.mods.clear()
        part.stock.clear()
    
        part.delete_instance()

@app.route('/api/parts/', methods=['DELETE'])
def delete_part():
    data = request.args
    
    __stock_delete_part(data.get('id', None))
    
    return {}

@app.route('/api/parts/footprint/', methods=['GET'])
def get_footprint():
    name = request.args.get('name', None)
    if name:
        folder, filename = name.split('=')
        path = '/Users/fefa4ka/Development/_clone/kicad/kicad-footprints/' + folder + '.pretty/' + filename + '.kicad_mod'
        file = open(path, 'r')
        data = '\n'.join(file.readlines())
        file.close()
    else:
        data = defaultdict(list)
        for file in glob.glob('/Users/fefa4ka/Development/_clone/kicad/kicad-footprints/*.pretty/*.kicad_mod'):
            category, footprint = file.split('/')[-2:]
            data[category.replace('.pretty', '')].append(footprint.replace('.kicad_mod', ''))
    
    return data


@app.route('/api/parts/footprints/', methods=['GET'])
def get_footprints():
    data = defaultdict(list)
    query = request.args.get('query', None)
    if query:
        query = query.lower()

    for file in glob.glob('/Users/fefa4ka/Development/_clone/kicad/kicad-footprints/*.pretty/*.kicad_mod'):
        category, footprint = file.split('/')[-2:]
        category = category.replace('.pretty', '')
        footprint = footprint.replace('.kicad_mod', '')

        if not query or (category.lower().find(query) != -1 or footprint.lower().find(query) != -1):
            data[category].append(footprint)
    
    return data

@app.route('/api/blocks/<name>/part_params/', methods=['GET'])
def get_part_params(name):
    params = request.args
    
    Block = Build(name, **params).block
    
    return {
        'spice': Block.spice_params,
        'part': {**Block.get_arguments(Block), **Block.get_params(Block)},
        'props': Build(name).base.props
    }

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True, threaded=True)
