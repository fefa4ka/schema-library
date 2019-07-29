from ..interface import Interfaced
from skidl import Part

class Modificator(Interfaced):
    USB = ['D-', 'D+']

    def usb(self, instance):
        self.interface('USB', instance)
