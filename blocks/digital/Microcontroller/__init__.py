from bem import Block, Build, u_B, u_Hz
from bem.abstract import Physical, Network
from skidl import Part, Net, TEMPLATE

class Base(Physical()):
    mods = {
        'vendor': ['Microchip_ATmega'],
        'series': ['ATmega8']
    }

    reset = None

    frequency = 8000000 @ u_Hz
    flash = 8 * 1024 @ u_B
    eeprom = 512 @ u_B
    sram = 1024 @ u_B

    # spice_params = {
    #     'MFlash': {'description': 'In-System Self-programmable Flash program memory', 'unit': {'suffix': 'B', 'name': 'byte'}, 'value': ''},
    # }

    def willMount(self, frequency=0 @ u_Hz):
        pass

    def circuit(self):
        self.element = self.part()
        pass


# MCU(vendor='Microchip_ATmega', series='ATmega8')(model='ATmega8L-16PU')
# cpu.I2C & 
        