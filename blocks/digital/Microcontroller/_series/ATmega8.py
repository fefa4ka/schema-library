from bem import Block, Net, u_V, u_uF, u_pF
from .. import Base
from bem.basic import Capacitor
from bem.basic.oscillator import Crystal
from bem.abstract import Network

pins = {}
pins['ATmega8-16PU'] = {
    'PD0': 'RX',
    'PD1': 'TX',
    'PD2': 'INT0',
    'PD3': 'INT1',
    'PD4': ['XCK', 'T0'],
    'PD5': 'T1',
    'PD6': 'AIN0',
    'PD7': 'AIN1',
    'PB0': 'ICP1',
    'PB1': 'OC1A',
    'PB2': ['SS', 'OC1B'],
    'PB3': ['MOSI', 'OC2'],
    'PB4': 'MISO',
    'PB5': 'SCK',
    'PB6': ['XTAL1', 'TOSC1'],
    'PB7': ['XTAL2', 'TOSC2'],
    'PC0': 'ADC0',
    'PC1': 'ADC1',
    'PC2': 'ADC2',
    'PC3': 'ADC3',
    'PC4': ['ADC4', 'SDA'],
    'PC5': ['ADC5', 'SCL']
}

pins['ATmega8U2'] = {
    'PB0': ['SS', 'PCINT0'],
    'PB1': ['SCLK', 'PCINT1'],
    'PB2': ['PDI', 'MOSI', 'PCINT2'],
    'PB3': ['PDO', 'MISO', 'PCINT3'],
    'PB4': ['T1', 'PCINT4'],
    'PB5': 'PCINT5',
    'PB6': 'PCINT6',
    'PB7': ['PCINT7', 'OC.0A', 'OC.1C'],
    'PC0': 'XTAL2',
    'PC1': ['RESET', 'dW'],
    'PC2': ['PCINT11', 'AIN2'],
    'PC4': ['PCINT10'],
    'PC5': ['PCINT9', 'OC.1B'],
    'PC6': ['OC.1A', 'PCINT8'],
    'PC7': ['INT4', 'ICP1', 'CLKO'],
    'PD0': ['OC.0B', 'INT0'],
    'PD1': ['AIN0', 'INT1'],
    'PD2': ['RXD1', 'AIN1', 'INT2'],
    'PD3': ['TXD1', 'INT3'],
    'PD4': ['INT5', 'AIN3'],
    'PD5': ['XCK', 'AIN4', 'PCINT12'],
    'PD6': ['RTS', 'AIN5', 'INT6'],
    'PD7': ['CTS', 'HWB', 'AIN6', 'T0', 'INT7']
}

class ATmega(Base):
    """
    The Atmel®AVR® ATmega8 is a low-power CMOS 8-bit microcontroller based on the AVR RISC
    architecture. By executing powerful instructions in a single clock cycle, the ATmega8 achieves
    throughputs approaching 1MIPS per MHz, allowing the system designer to optimize power consumption
    versus processing speed.
    """
    V = 5 @ u_V 

    def apply_part(self, part):
        super().apply_part(part)

        self.set_pins_aliases(self.pins_alias())

    def pins_alias(self):
        return pins[self.model]

    def circuit(self):
        ref = self.props.get('ref', self.name)
        self.element = self.part(ref=ref)

        # Power Supply
        v_stable = self.v_ref & (Capacitor()(0.1 @ u_uF)['+, -'] | Capacitor()(4.7 @ u_uF)['+, -']) & self.gnd
        self.v_ref += self['vcc'], self['avcc']
        self.gnd += self.element['gnd']
        if self['agnd']:
            self.gnd += self['agnd']

        # External resonator if frequency non 0
        if self.frequency != 0:
            oscillator = Crystal()(frequency=self.frequency)
            # Creating resonation circuit
            cap = self.gnd & Capacitor()(22 @ u_pF) \
                    & self['XTAL1'] \
                        & oscillator \
                    & self['XTAL2'] \
                & Capacitor()(22 @ u_pF) & self.gnd


class Modificator(Network(interface=['uart', 'spi', 'i2c']), ATmega):
    pass

