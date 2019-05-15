from bem import Block, Build, u_B, u_Hz
from skidl import Part, Net, TEMPLATE

class Base(Block):

    reset = None
    UART = None
    SPI = None

    speed = 8000000 @ u_Hz
    flash = 8 * 1024 @ u_B
    eeprom = 512 @ u_B
    sram = 1024 @ u_B

    spice_params = {
        'MFlash': {'description': 'In-System Self-programmable Flash program memory', 'unit': {'suffix': 'B', 'name': 'byte'}, 'value': ''},
    }

    @property
    def spice_part(self):
        return None

    @property
    def part(self):
        part = Part('MCU_' + self.vendor, self.model, footprint=self.footprint, dest=TEMPLATE)
    
        return part

# MCU(vendor='ATmega8A', speed=10 @ u_Hz, EEPROM=512 @ u_B)
        