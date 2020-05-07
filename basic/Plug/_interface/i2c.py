from .. import Base
from bem.abstract import Network

class Modificator(Network(interface='i2c'), Base):
    pass

