import inspect
import glob
from builtins import open
from math import isnan
from flask import request
from flask_api import FlaskAPI
from PySpice.Unit.Unit import UnitValue
from skidl import Circuit
from collections import defaultdict
from bem import Build

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

app = FlaskAPI(__name__)


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

@app.route('/api/blocks/<name>/', methods=['GET'])
def block(name):
    # Reset default circuit
    builtins.default_circuit = Circuit()

    mods = request.args
    Block = Build(name, **mods).block
    arguments = Block.get_arguments(Block)
    props = {}
    for attr in arguments:
        props[attr] = getattr(Block, attr)

        arg = mods.get(attr, None)

        if arg and not isnan(float(arg)):
            if type(props[attr]) in [int, float]:
                props[attr] = float(arg)
            else:
                props[attr]._value = float(arg)
        
    Instance = Block(**props)
    
    parts = []
    for part in Instance.input.circuit.parts:
        pins = [str(pin) for pin in part.get_pins()]
        parts.append({
            'name': part.name,
            'description': part.description,
            'pins': pins
        })

    nets = {}
    for net in Instance.input.circuit.get_nets():
        pins = [str(pin) for pin in net.get_pins()]
        nets[net.name] = pins

    return {
        'name': Block.name,
        'mods': Block.mods,
        'description': Block.get_description(Block),
        'args': Instance.get_arguments(),
        'params': Instance.get_params(),
        'pins': Instance.get_pins(),
        'parts': parts,
        'nets': nets
    }

if __name__ == "__main__":
    app.run(debug=True)
