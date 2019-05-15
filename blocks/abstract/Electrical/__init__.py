from bem import u, Block
from bem.abstract import Network
from bem.tester import BuildTest
from PySpice.Unit import u_V, u_Ohm, u_A, u_W, u_S, u_s
from lcapy import R

class Base(Block):
    inherited = [Network]
    mods = {
        'port': 'one'
    }

    V = 10 @ u_V
    Power = 0 @ u_W
    Load = 1000 @ u_Ohm  # [0 @ u_Ohm, 0 @ u_A, 0 @ u_W]

    doc_methods = ['willMount', 'circuit']

    element = None
    ref = ''

    def __init__(self, *args, **kwargs):
        is_ciruit_building = kwargs.get('circuit', True)
        if kwargs.get('circuit', None) != None:
            del kwargs['circuit']

        self.load(self.V)

        super().__init__(*args, **kwargs)

        if self.Power and not hasattr(self, 'P'):
            self.consumption(self.V)

        if is_ciruit_building:
            self.circuit()


    def willMount(self, V=None, Load=None):
        """
            V -- Volts across its input terminal and gnd
            V_out -- Volts across its output terminal and gnd
            G -- Conductance `G = 1 / Z`
            Z -- Input unloaded impedance of block
            P -- The power dissipated by block
            I -- The current through a block
            I_load -- Connected load presented in Amperes
            R_load -- Connected load presented in Ohms
            P_load -- Connected load presented in Watts
        """
        pass

    # Circuit Creation
    def circuit(self, *args, **kwargs):
        element = self.part(*args, **kwargs)
       
        if element:
            element.ref = self.ref or element.ref 
            self.element = element
            
            self.input += self.element[1]
            self.output += self.element[2]
    

    # Consumption and Load
    def consumption(self, V):
        self.P = None
        self.I = None
        self.Z = None

        if self.Power == 0 @ u_Ohm or V == 0:
            return

        Power = self.Power
        
        if Power.is_same_unit(1 @ u_Ohm):
            self.Z = Power
            self.I = V / self.Z
        
        if Power.is_same_unit(1 @ u_W):
            self.P = Power
            self.I = self.P / V
        else:
            if Power.is_same_unit(1 @ u_A):
                self.I = Power

            self.P = V * self.I

        if not self.Z:
            self.Z = V / self.I

        self.G = (1 / self.Z) @ u_S

    def load(self, V_load):
        Load = self.Load
        
        if type(Load) in [int, float] or Load.is_same_unit(1 @ u_Ohm):
            Load = self.Load = Load @ u_Ohm
            self.R_load = Load
            self.I_load = V_load / self.R_load
        
        if Load.is_same_unit(1 @ u_W):
            self.P_load = Load
            self.I_load = self.P_load / V_load
        else:
            if Load.is_same_unit(1 @ u_A):
                self.I_load = Load

            self.P_load = V_load * self.I_load

        if not hasattr(self, 'R_load'):
            self.R_load = V_load / self.I_load
        
        if not hasattr(self, 'Z_load'):
            self.Z_load = R(self.R_load)

        self.load_args = {
            'V': V_load,
            'Load': self.Load
        } 
        
    def current(self, voltage, impedance):
        return voltage / impedance

    def power(self, voltage, impedance):
        return voltage * voltage / impedance


    def part(self, *args, **kwargs):
        return self.part_spice(*args, **kwargs)

    def part_spice(self, *args, **kwargs):
        return None
        
    def simulate(self, sources=None, load=None):
        Test = BuildTest(self.__class__, **(self.mods))
        Test._sources = sources
        Test._load = load

        arguments = self.__class__.get_arguments(self.__class__, self)
        simulation = Test.simulate(arguments)

        return simulation
      