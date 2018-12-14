import os
# KiCad Modules directory
os.environ['KISYSMOD'] = '/Users/fefa4ka/Development/_clone/kicad/modules'
# Path where is libngspice.dylib placed
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/Cellar/libngspice/28/lib/'

from skidl.pyspice import *

Enviroment = {
    'V': V(ref='VS', dc_value=5 @ u_V),
    'R': R,
    'gnd': gnd
}

BLOCKS_PATH = 'blocks'
