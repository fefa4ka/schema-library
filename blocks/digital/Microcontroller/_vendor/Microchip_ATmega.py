from bem import Net
from bem.abstract import Network

class Modificator(Network(interface=['uart', 'spi', 'i2c'])): 
    pass