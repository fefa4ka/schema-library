from ..interface import Interfaced
from skidl import Part

class Modificator(Interfaced):
    UART = ['TX', 'RX']

    def uart(self, instance):
        rx = self['RX']
        tx = self['TX']
        
        rx += instance['TX']
        tx += instance['RX']
          
    def uart_connector(self):
        connector = Part('Connector_Generic', 'Conn_01x03', footprint='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', ref='UART')

        connector[1] += self['RX']
        connector[2] += self['TX']
        connector[3] += self.gnd
