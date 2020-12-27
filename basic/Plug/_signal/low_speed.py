from .. import Base
from bem.abstract import Physical, Virtual

class Modificator(Physical()):
    def __init__(self, *args, **kwargs):
        rows = self.props.get('rows', 1)
        columns = self.props.get('columns', 1)

        connector_type = self.props.get('type', 'Male').capitalize()

        self.props['part'] = 'Connector:Conn_{0:02d}x{1:02d}_{2}'.format(rows, columns, connector_type)

        if connector_type == 'Male':
            footprint_lib = 'PinHeader'
        else:
            footprint_lib = 'PinSocket'

        self.props['footprint'] = 'Connector_{0}_2.54mm:{0}_{1}x{2:02d}_P2.54mm_Horizontal'.format(footprint_lib, rows, columns)

        super().__init__(*args, **kwargs)

