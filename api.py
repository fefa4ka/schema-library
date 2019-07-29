import datetime
import glob
import os
from collections import defaultdict
from math import isnan

from flask import request, Response
from flask_api import FlaskAPI

from PySpice.Unit import u_A, u_Hz, u_ms, u_Ohm, u_s, u_V
from PySpice.Unit.Unit import UnitValue
from skidl import Circuit, Net, search, subcircuit, set_default_tool, set_backup_lib, KICAD, SPICE

from bem import Build, bem_scope
from bem.abstract import Physical
from bem.model import Part, Pin, Param, Mod, Prop, Stock
from bem.printer import Print
from bem.simulator import Simulate, set_spice_enviroment
from probe.read import get_sigrok_samples
from probe import get_arg_units, get_minimum_period
from probe.source import JDS6600, KA3005P, simulation_sources
from bem.tester import BuildTest
from copy import copy
from subprocess import PIPE, run
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
        device = Physical(part=name.replace('.lib', ''))().element

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
    blocks = bem_scope()

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
        props = Block.parse_arguments(params)

        Instance = Block(**props)

        parts = {}
        nets = {}

        if hasattr(Instance, 'input') and Instance.input:
            if type(Instance.input) == list:
                circuit = Instance.input[0].circuit
            else:
                circuit = Instance.input.circuit
            for part in circuit.parts:
                pins = [str(pin).split(',')[0] for pin in part.get_pins() or []]
                value = copy(part.value)
                if type(value) not in [str, int, float]:
                    value = value.canonise()
                    value._value = int(value._value)


                parts[part.ref] = {
                    'name': part.name,
                    'description': str(value) + '|' + part.description.replace(',', ';'),
                    'pins': pins
                }

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

        if hasattr(Instance, 'devices'):
            devices = Instance.devices()
        else:
            devices = []

        params = {
            'name': Block.name,
            'mods': { **Block.mods, **{ key: prop for key, prop in Block.props.items() if key in props.keys() }},
            'props': props,
            'description': Block.get_description(Block),
            'params_description': Block.get_params_description(Block),
            'args': Instance.get_arguments(),
            'params': Instance.get_params(),
            'pins': Instance.get_pins(),
            'files': Block.files,
            'parts': parts,
            'nets': nets,
            'body_kit': params.get('body_kit', Test.body_kit()),
            'pcb_body_kit': params.get('pcb_body_kit', Print.body_kit(Instance)),
            'available': available,
            'devices': devices
        }

        params['params'] = {param: params['params'][param] for param in params['params'].keys() if not params['args'].get(param, None)}

        return params

    params = build()
    return params

@app.route('/api/blocks/<name>/netlist/<type>/', methods=['POST'])
def netlist(name, type):
    params = request.data

    Block = Build(name, **params['mods']).block
    props = Block.parse_arguments(params['args'])
    body_kit = params.get('pcb_body_kit', [])

    netlist = Print(Block, props, body_kit, type).netlist()

    return netlist

@app.route('/api/blocks/<name>/simulate/', methods=['POST'])
def simulate(name):
    params = request.data
    Block = Build(name, **params['mods']).block
    args = Block.parse_arguments(params['args'])
    Instance = Block(**args)

    body_kit = params.get('body_kit', None)

    simulation = Instance.simulate(body_kit)

    return simulation


@app.route('/api/blocks/<name>/simulate/cases/', methods=['POST'])
def simulate_cases(name):
    params = request.data
    Block = Build(name, **params['mods']).block
    Test = BuildTest(Block, **params['mods'])

    cases = {}
    for name in Test.cases():
        set_spice_enviroment()
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

        pins = defaultdict(lambda: defaultdict(list))
        for pin in part.pins:
            # pins[pin.block_pin].append({
            #     'pin': pin.pin,
            #     'unit': pin.unit
            # })
            pins[pin.unit][pin.block_pin].append(pin.pin)

        parts.append({
            'id': part.id,
            'block': part.block,
            'model': part.model,
            'library': part.library,
            'symbol': part.symbol,
            'footprint': part.footprint,
            'mods': [mod.name + ':' + mod.value for mod in part.mods],
            'props': [prop.name + ':' + prop.value for prop in part.props],
            'params': params,
            'spice': '',
            'spice': part.spice,
            'pins': pins,
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
        library=data.get('library', ''),
        symbol=data.get('symbol', ''),
        footprint=data['footprint'],
        datasheet=data.get('datasheet', ''),
        description=data.get('description', ''),
        spice=data.get('spice', '')
    )
    part.save()
    
    units = data.get('pins', {})
    for unit in units.keys():
        pins = units[unit].keys()
        for block_pin in pins:
            part_pins = units[unit][block_pin]
            for part_pin in part_pins:
                pin = Pin(unit=unit, pin=part_pin, block_pin=block_pin)
                pin.save()
                part.pins.add(pin)

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

    spice = defaultdict(str)
    for part in Part.select():
        if part.spice:
            spice[part.symbol] += '\n*\n' + part.spice

    for symbol in spice.keys():
        spice_file = open('./spice/' + symbol + '.lib', 'w')
        spice_file.write('*\n' + spice[symbol] + '\n*')
        spice_file.close()

    return  { 'part': part.id }

def __stock_delete_part(part_id):
    part = Part.get_or_none(id=part_id)

    if part:
        part.params.clear()
        part.mods.clear()
        part.props.clear()
        part.stock.clear()
        part.pins.clear()

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
    body_kit = req.get('body_kit', [])

    for index, block in enumerate(body_kit):
        mods = {}
        if block.get('mods', None):
            mods = block['mods']

        ref = block['name'].split('.')[-1] + '_' + str(index)
        BlockModel = Build(block['name'], **mods, ref=ref).block
        args = BlockModel.parse_arguments(block['args'])
        BlockInstance = BlockModel(**args)

        if hasattr(BlockInstance, 'set_device'):
            BlockInstance.set_device()

    probes = req.get('probes', [])

    period = get_minimum_period(body_kit)
    end_time = period * 4
    step_time = period / 200

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


@app.route('/api/parts/pins/', methods=['GET'])
def get_pins():
    from skidl import Part
    set_default_tool(KICAD)
    builtins.SIMULATION = False

    library = request.args.get('library', None)
    symbol = request.args.get('symbol', None)

    part = Part(library, symbol)

    return [str(pin) for pin in part.pins]


@app.route('/api/parts/footprint/', methods=['GET'])
def get_footprint():
    name = request.args.get('name', None)

    if name:
        folder, filename = name.split(':')
        path = '/Users/fefa4ka/Development/_clone/kicad/kicad-footprints/' + folder + '.pretty/' + filename + '.kicad_mod'
        # file = open(path, 'r')
        # data = '\n'.join(file.readlines())
        # file.close()
        command = ['node', 'bem/mod2svg.js', path]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        # print(result)
        data = result.stdout
        data = Response(data)
        data.headers['Content-Type'] = 'image/svg+xml'
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

    props = {}
    if Build(name).base:
        props = Build(name).base.props
        props = { key: value if type(value) == list else [value] for key, value in props.items() }

    return {
        'spice': Block.spice_params if hasattr(Block, 'spice_params') else{},
        'pins': list(Block.pins.keys()) if type(Block.pins) == dict else list(Block.pins().keys()),
        'part': {**Block.get_arguments(Block), **Block.get_params(Block)},
        'props': props
    }

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True, threaded=True, host='0.0.0.0')
