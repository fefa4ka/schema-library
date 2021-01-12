from .ATmega8 import ATmega
from bem.basic import Capacitor
from bem import u_uF

pins = {
    'PB0': ['SS', 'PCINT0'],
    'PB1': ['SCK', 'SCLK', 'PCINT1'],
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
    'PD2': ['RX', 'RXD1', 'AIN1', 'INT2'],
    'PD3': ['TX', 'TXD1', 'INT3'],
    'PD4': ['INT5', 'AIN3'],
    'PD5': ['XCK', 'AIN4', 'PCINT12'],
    'PD6': ['RTS', 'AIN5', 'INT6'],
    'PD7': ['CTS', 'HWB', 'AIN6', 'T0', 'INT7']
}


class Modificator(ATmega):
    mods = { 'interface': ['uart', 'i2c', 'spi', 'usb'] }
    def pins_alias(self):
        return pins

    def usb(self, instance):
        super().usb(instance)

        self['UVCC'] & instance.v_ref
        self['UCAP'] & Capacitor()(1 @ u_uF) & self['UGND'] & instance.gnd
