import io
from contextlib import redirect_stdout

from PySpice.Unit import u_ms, u_s
from skidl import (KICAD, SPICE, Circuit, Net, search, set_default_tool, set_backup_lib,
                   subcircuit)

from settings import default_temperature

from . import Block, u

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

libs = ['./spice/']


class Simulate:
    block = None
    circuit = None
    simulation = None
    node = None

    SIMULATE = False
    spice_params = {}

    def __init__(self, block, libs=libs):
        self.block = block
        
        from skidl.tools.spice import node
        self.circuit = builtins.default_circuit.generate_netlist(libs=libs)
        self.node = node

        print(self.circuit)

    def measures(self, analysis):
        index_field = None
        index = None

        if hasattr(analysis, 'time'):
            index_field = 'time'
            index = analysis.time
        else:
            index_field = 'sweep'
            index = analysis.sweep

        pins = self.block.get_pins().keys()
        
        current_branches = analysis.branches.keys()
    
        voltage = {}
        for pin in pins:
            try: 
                net = getattr(self.block, pin)
                if net and pin != 'gnd' and net != self.block.gnd:
                    node = self.node(net)
                    voltage[pin] = analysis[node]
            except:
                pass

        current = {}
        for branch in current_branches:
            current[branch] = -analysis[branch]

        data = []
        for index, entity in enumerate(index):
            entry = {
                index_field: entity.value * entity.scale
            }
            
            for key in voltage.keys():
                entry['V_' + key] = voltage[key][index].scale * voltage[key][index].value
                
            for key in current.keys():
                entry['I_' + key] = current[key][index].scale * current[key][index].value

            data.append(entry)

        return data

    def transient(self, step_time=0.01 @ u_ms, end_time=200 @ u_ms):
        self.simulation = self.circuit.simulator()
        analysis = self.simulation.transient(step_time=step_time, end_time=end_time) 
       
        return self.measures(analysis) 

    def dc(self, params, temperature=None):
        pins = self.block.get_pins().keys()
        measures = {}
        for temp in temperature or default_temperature:
            simulation = self.circuit.simulator(temperature=temp, nominal_temperature=temp)

            analysis = simulation.dc(**params)
            measures[u(temp)] = self.measures(analysis)

        return measures

    def ac(self, params, temperature=None):
        pins = self.block.get_pins().keys()
        measures = {}
        for temp in temperature or default_temperature:
            simulation = self.circuit.simulator(temperature=temp, nominal_temperature=temp)
            analysis = simulation.ac(**params)
            measures[temp] = analysis
     
        return measures


def set_spice_enviroment():
    set_backup_lib('.')
    set_default_tool(SPICE) 
    builtins.SIMULATION = True
    
    scheme = Circuit()
    builtins.default_circuit.reset(init=True)
    del builtins.default_circuit
    builtins.default_circuit = scheme
    builtins.NC = scheme.NC
