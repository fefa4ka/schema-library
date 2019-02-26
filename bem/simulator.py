import io
from contextlib import redirect_stdout

from skidl.tools.spice import node

from bem import Block, u_ms

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

libs = ['./spice/']


class Simulate:
    block = None
    simulation = None
    node = None

    SIMULATE = False
    spice_params = {}

    def __init__(self, block):
        self.block = block

    def run(self, libs=libs):
        # f = io.StringIO()
        # with redirect_stdout(f):
        circuit = builtins.default_circuit.generate_netlist(libs=libs) 
        self.simulation = circuit.simulator()

        # out = f.getvalue()
        print(circuit)
        
        self.node = node


    def pins(self, current_nodes=[], libs=libs, step_time=0.01 @ u_ms, end_time=200 @ u_ms):
        self.run(libs)

        waveforms = self.simulation.transient(step_time=step_time, end_time=end_time) 
        time = waveforms.time 
        
        pins = self.block.get_pins().keys()
    
        voltage = {}
        for pin in pins:
            try: 
                net = getattr(self.block, pin)
                if net and pin != 'gnd' and net != self.block.gnd:
                    node = self.node(net)
                    voltage[pin] = waveforms[node]
            except:
                pass

        current = {}
        for node in current_nodes:
            current[node] = -waveforms[node]
            
        data = []
        errors = []
        for index, time in enumerate(time):
            entry = {
                'time': time.value * time.scale
            }
            
            for key in voltage.keys():
                entry['V_' + key] = voltage[key][index].scale * voltage[key][index].value
                
            for key in current.keys():
                entry['I_' + key] = current[key][index].scale * current[key][index].value

            error = self.block.test(self.block).cases(entry)
            if error: 
                entry['error'] = error
    
            data.append(entry)

        return data
