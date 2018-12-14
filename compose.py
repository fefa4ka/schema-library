from settings import *
from bem import Loader

# Template
divider = Loader('Divider', Enviroment, type='resistive').block(V_in=10 @ u_V, V_out=5 @ u_V)


# Circuit
input = Enviroment['V']
input['n'] += Enviroment['gnd']

output = Net('Divided')
divider.make(input['p'], output)


# Simulate the circuit.
circ = generate_netlist()              # Translate the SKiDL code into a PyCircuit Circuit object.
sim = circ.simulator()                 # Create a simulator for the Circuit object.
dc_vals = sim.dc(VS=slice(0, 1, 0.1)) 
