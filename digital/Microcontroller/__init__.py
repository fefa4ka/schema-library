from bem import Block, Build, u_B, u_Hz
from bem.abstract import Physical, Network
from skidl import Part, Net, TEMPLATE

class Base(Physical()):
    reset = None

    frequency = 8000000 @ u_Hz
    flash = 8 * 1024 @ u_B
    eeprom = 512 @ u_B
    sram = 1024 @ u_B

    def willMount(self, frequency=0 @ u_Hz):
        pass


