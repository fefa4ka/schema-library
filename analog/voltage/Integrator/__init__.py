from bem.abstract import Electrical
from bem.basic import Resistor, Capacitor, OpAmp
from bem.analog.voltage import Divider
from bem import u_Hz, u_Ohm, u_kOhm, u_F
from math import pi

class Base(Electrical()):
    pass
