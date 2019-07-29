from .. import Base

class Modificator(Base):
    pins = {
        'v_ref': ('Input', ['input', 'output']),
        'gnd': True
    }
