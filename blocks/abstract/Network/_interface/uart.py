from ..interface import Interfaced
from skidl import Part

class Modificator(Interfaced):
    UART = ['TX', 'RX']

    def uart(self, instance):
        print('CONNNECT UAAARTTT')
        rx = self['RX']
        tx = self['TX']
        
        rx += instance['TX']
        tx += instance['RX']
   
