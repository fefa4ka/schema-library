from .. import Base
from bem import Resistor, Capacitor, u, u_F, u_Hz
from skidl import Net
from math import pi


class Modificator(Base):
    """**Split Supply**
 
    Because signals often are “near ground” it is convenient to use symmetrical positive and negative supplies. This simplifies biasing and eliminates coupling capacitors.

    Warning: you must always provide a dc path for base bias current, even if it goes only to ground. In this circuit it is assumed that the signal source has a dc path to ground. If not (e.g., if the signal is capacitively coupled), you must pro- vide a resistor to ground. `R_b` could be about one-tenth of `β * R_e`, as before.

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 84
    """

    def circuit(self):
        self.input_n = Net()
        
        super().circuit()


    def test_sources(self):
        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 120,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }, {
                'name': 'V',
                'args': {
                    'value': {
                        'value': 15,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_ref'],
                    'n': ['gnd']
                }
        }, {
                'name': 'V_1',
                'args': {
                    'value': {
                        'value': -15,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['input_n'],
                    'n': ['gnd']
                }
        }]