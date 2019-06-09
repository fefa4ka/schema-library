from . import Base
from types import MethodType 

class Interfaced(Base):
    interfaces = []
    pins = {
        'v_ref': True,
        'gnd': True 
    }

    def __and__(self, instance):
        if issubclass(type(instance), Base):
            self.__series__(instance)

            return instance
            
        if isinstance(instance, MethodType):
            return instance(self)

        raise Exception

    def __rand__(self, instance):
        if issubclass(type(instance), Base):
            instance.__series__(self)

            return instance

        if isinstance(instance, MethodType):
            return instance(self)
            
        raise Exception

    def __or__(self, instance):
        raise Exception 

    def __series__(self, instance):
        for protocol in instance.mods['interface']: 
            if protocol in self.mods['iterface']:
                interface = getattr(self, protocol)
                interface(instance)
                
        self.connect_power_bus(instance)

    def get_interface_pins(self, protocol):
        pins = {}
        for pin in getattr(self, protocol.upper()):
            pins[pin] = self[pin]

        return pins

    def interface(self, protocol, instance):
        for pin in getattr(self, protocol.upper()):
            self_pin = self[pin]
            self_pin += instance[pin]
        
# cpu.spi & Display --  cpu.spi(Display) cpu.interface(spi, Display.interfaces['spi'])