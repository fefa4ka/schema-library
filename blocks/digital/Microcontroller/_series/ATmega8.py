from bem import Block, Net, u_uF, u_pF
from bem.basic import Capacitor, Oscillator

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

class Modificator(Block):
    """
    The Atmel®AVR® ATmega8 is a low-power CMOS 8-bit microcontroller based on the AVR RISC
    architecture. By executing powerful instructions in a single clock cycle, the ATmega8 achieves
    throughputs approaching 1MIPS per MHz, allowing the system designer to optimize power consumption
    versus processing speed.
    """

    def apply_part(self, part):
        super().apply_part(part)

        self.set_pins_aliases(pins[self.model])

    def circuit(self):
        ref = self.props.get('ref', self.name)
        self.element = self.part(ref=ref)

        # Power Supply
        v_stable = self.v_ref & (Capacitor()(0.1 @ u_uF)['+, -'] | Capacitor()(4.7 @ u_uF)['+, -']) & self.gnd
        self.v_ref += self['vcc'], self['avcc']
        self.gnd += self.element['gnd'], self['agnd']

        # External resonator if frequency non 0
        if self.frequency != 0:
            oscillator = Oscillator(type='crystal')(frequency=self.frequency)
            # Creating resonation circuit
            cap = self.gnd & Capacitor()(22 @ u_pF) \
                    & self['XTAL1'] \
                        & oscillator \
                    & self['XTAL2'] \
                & Capacitor()(22 @ u_pF) & self.gnd
        