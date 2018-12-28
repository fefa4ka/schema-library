from bem import Block, Build
from PySpice.Unit import u_kOhm, u_V

class Base(Block):
    # Props
    V_in = 0
    V_out = 0