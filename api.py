import datetime
import glob
import os
from collections import defaultdict
from math import isnan

from flask import request
from flask_api import FlaskAPI

from PySpice.Unit import u_A, u_Hz, u_ms, u_Ohm, u_s, u_V
from PySpice.Unit.Unit import UnitValue
from skidl import Circuit, Net, search, subcircuit, set_default_tool, set_backup_lib, KICAD, SPICE

from bem import Build, get_bem_blocks
from bem.model import Part, Param, Mod, Prop, Stock
from bem.printer import Print
from bem.simulator import Simulate
from probe.read import get_sigrok_samples
from probe import get_arg_units, get_minimum_period
from probe.source import JDS6600, simulation_sources
from bem.tester import BuildTest

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

app = FlaskAPI(__name__)

builtins.SIMULATION = True


@app.route('/api/devices/', methods=['GET'])
def devices():
    set_default_tool(KICAD)
    builtins.SIMULATION = False

    import io
    from contextlib import redirect_stdout

    keyword = request.args.get('query', None)
    name = request.args.get('name', None)
    
    if keyword:
        f = io.StringIO()
        with redirect_stdout(f):
            search(keyword)

        out = f.getvalue()
        
        devices = out[out.rfind('\r') + 2:].split('\n')
        result = defaultdict(list)

        for device in devices:
            if device:
                lib, device = device.split(':')
                lib = lib.replace('.lib', '')
                description_pos = device.find('(')
                title = device[:description_pos].strip()
                description = device[description_pos + 1: -2].strip()
                result[lib].append([title, description])

        return result

    if name:
        device = Build(name.replace('.lib', '')).element

        return {
            'library': device.lib,
            'name': device.name,
            'description': device.description,
            'pins': [pin.name for pin in device.pins]
        }


@app.route('/api/sources/', methods=['GET'])
def sources():
    sources = simulation_sources()
    return sources


@app.route('/api/blocks/', methods=['GET'])
def blocks():
    blocks = get_bem_blocks()

    return blocks


@app.route('/api/blocks/<name>/', methods=['GET'])
def block(name):
    set_backup_lib('.')
    set_default_tool(KICAD) 
    builtins.SIMULATION = False
    
    scheme = Circuit()
    builtins.default_circuit.reset(init=True)
    del builtins.default_circuit
    builtins.default_circuit = scheme
    builtins.NC = scheme.NC


    gnd = Net('0')
    gnd.fixed_name = True

    def build():
        params = request.args
        Block = Build(name, **params).block
        props = Block.parse_args(Block, params)
        
        Instance = Block(**props)
        
        parts = []
        nets = {}

        if Instance.input:
            if type(Instance.input) == list:
                circuit = Instance.input[0].circuit
            else:
                circuit = Instance.input.circuit
            for part in circuit.parts:
                pins = [str(pin).split(',')[0] for pin in part.get_pins() or []]
                parts.append({
                    'name': part.name,
                    'description': part.description,
                    'pins': pins
                })

            for net in circuit.get_nets():
                pins = [str(pin).split(',')[0] for pin in net.get_pins() or []]
                nets[net.name] = pins
        
        RawBlock = Build(Block.name)
        props = RawBlock.base and RawBlock.base.props
        Test = BuildTest(Block, **params)
        if hasattr(Instance, 'selected_part'):
            available = [{'id':part.id, 'model':part.model, 'footprint':part.footprint} for part in Instance.available_parts()]
        else:
            available = []
            
        params = {
            'name': Block.name,
            'mods': { **Block.mods, **{ key: prop for key, prop in Block.props.items() if key in props.keys() }},
            'props': props,
            'description': Block.get_description(Block),
            'params_description': Block.get_params_description(Block),
            'args':  Block.get_arguments(Block, Instance),
            'params': Instance.get_params(),
            'pins': Instance.get_pins(),
            'files': Block.files,
            'parts': parts,
            'nets': nets,
            'sources': params.get('sources', Test.sources()),
            'load': params.get('load', Test.load()),
            'devices': params.get('devices', Print.additional_devices(Instance)),
            'available': available
        }

        params['params'] = {param: params['params'][param] for param in params['params'].keys() if not params['args'].get(param, None)}
        
        return params

    params = build()
    return params

@app.route('/api/blocks/<name>/netlist/', methods=['POST'])
def netlist(name):
    params = request.data
    
    Block = Build(name, **params['mods']).block
    props = Block.parse_args(Block, params['args'])
    kit = params.get('devices', [])
    
    netlist = Print(Block, props, kit).netlist()

    return netlist

@app.route('/api/blocks/<name>/simulate/', methods=['POST'])
def simulate(name):
    params = request.data
    Block = Build(name, **params['mods']).block
    Test = BuildTest(Block, **params['mods'])
    simulation = Test.simulate(params['args'])

    return simulation 

@app.route('/api/blocks/<name>/simulate/cases/', methods=['POST'])
def simulate_cases(name):
    params = request.data
    Block = Build(name, **params['mods']).block
    Test = BuildTest(Block, **params['mods'])

    cases = {}
    for name in Test.cases():
        case = getattr(Test, name)
        cases[name] = case(params['args'])
        cases[name]['description'] = Test.description(name)

    return cases  

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
            'scheme': part.scheme,
            'footprint': part.footprint,
            'mods': [mod.name + ':' + mod.value for mod in part.mods],
            'props': [prop.name + ':' + prop.value for prop in part.props],
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
        scheme=data.get('scheme', ''),
        footprint=data['footprint'],
        datasheet=data.get('datasheet', ''),
        description=data.get('description', ''),
        spice=data.get('spice', '')
    )
    part.save()
    
    mods = []
    for mod in data.get('mods', []):
        name, value = mod.split(':')
        mod = Mod(name=name, value=value)
        mod.save()
        part.mods.add(mod)

    props = []
    for prop in data.get('props', []):
        name, value = prop.split(':')
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
        part.props.clear()
        part.stock.clear()
    
        part.delete_instance()

@app.route('/api/parts/', methods=['DELETE'])
def delete_part():
    data = request.args
    
    __stock_delete_part(data.get('id', None))
    
    return {}

@app.route('/api/probes/', methods=['GET'])
def get_analys_devices():
    import subprocess
    la = 'sigrok-cli'
    # devices = [device.split(' - ') for device in subprocess.getoutput(la + ' --scan').split('\n')[1:]]
    # devices = [{
    #     'name': device[0],
    #     'description': device[1].split(':')[0].strip(),
    #     'pins': device[1].split(':')[1].strip().split(' ')
    # } for device in devices]p

    devices = [{
        'name': 'fx2lafw',
        'description': 'Logic Analyzer - 8 channel',
        'pins': ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
    }, {
        'name': 'rigol-ds',
        'description': 'Oscilloscope - 2 channel',
        'pins': ['CH1', 'CH2']
    }, {
        'name': 'demo',
        'description': 'Demo',
        'pins': ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'A0', 'A1', 'A2', 'A3']
    }]
    return devices

@app.route('/api/serial/', methods=['GET'])
def get_serial_ports():
    from bem.prober import serial_ports

    return serial_ports()

@app.route('/api/probes/', methods=['POST'])
def get_probes():
    req = request.data
    sources = req.get('sources', [])
    for source in sources:
        port = source.get('port', None)
        if port:
            args = {}
            part_name = source['name'].split('_')[0]
            part = Build(part_name).spice
            
            for arg in source['args'].keys():
                if source['args'][arg]['value']:
                    try: 
                        args[arg] = float(source['args'][arg]['value']) @ get_arg_units(part, arg)
                    except:
                        args[arg] = source['args'][arg]['value']
            
            device = JDS6600(port=port)
            if hasattr(device, source['name']):
                generator = getattr(device, source['name'])
                generator(
                    channel=source.get('channel', 1),
                    **args)

    probes = req.get('probes', [])
    
    period = get_minimum_period(sources)
    end_time = period * 10
    step_time = period / 50
    
    devices = defaultdict(list)
    pins = {}
    for probe in probes:
        pins[probes[probe]['name'] + probes[probe]['channel']] = probe
        devices[probes[probe]['name']].append(probes[probe]['channel'])
    
    data = {}
    for device in devices.keys():
        device_data = get_sigrok_samples(device, ','.join(devices[device]), step_time @ u_s, end_time @ u_s)
        for ch in device_data.keys():
            probe = pins[device + ch]
            data[probe] = device_data[ch]

    chartData = [{'time':step * step_time} for step in range(int(end_time / step_time))]
    for index, entity in enumerate(chartData):
        for probe in data.keys():
            chartData[index]['V_' + probe] = data[probe][index]
        
    return chartData

@app.route('/api/parts/footprint/', methods=['GET'])
def get_footprint():
    name = request.args.get('name', None)
    if name:
        folder, filename = name.split(':')
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
        'spice': Block.spice_params if hasattr(Block, 'spice_params') else {},
        'part': {**Block.get_arguments(Block), **Block.get_params(Block)},
        'props': Build(name).base and Build(name).base.props
    }

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True, threaded=True, host='0.0.0.0')
