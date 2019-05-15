from .. import Base
from bem import Net

class Modificator(Base):
    spice_params = {
        'RF': {'title': 'β_f', 'description': 'Ideal maximum forward beta', 'unit': {'suffix': '', 'name': 'number'}, 'value': ''},
    }

    pass    