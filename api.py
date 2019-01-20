import inspect

from flask import request
from flask_api import FlaskAPI

from bem import Build
from builtins import open

from PySpice.Unit.Unit import UnitValue

from skidl import Circuit
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

app = FlaskAPI(__name__)

@app.route('/blocks/<name>/', methods=['GET'])
def block(name):
    # Reset default circuit
    builtins.default_circuit = Circuit()

    mods = request.args
    Block = Build(name.capitalize(), **mods).block
    arguments = Block.get_arguments(Block)
    props = {}
    for attr in arguments:
        props[attr] = getattr(Block, attr)

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
        'args': arguments,
        'pins': Block.get_pins(Block),
        'parts': parts,
        'nets': nets
    }

if __name__ == "__main__":
    app.run(debug=True)
