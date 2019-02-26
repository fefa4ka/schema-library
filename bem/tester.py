from bem import Block
from settings import test_sources, test_load


class Test:
    block = None
    def __init__(self, block):
        self.block = block

    def cases(self, probes):
        pass

    def sources(self):
        sources = test_sources
        
        gnd = ['gnd']
        if len(self.load()) == 0:
            gnd.append('output')

        sources[0]['pins']['n'] = gnd

        return sources
    
    def load(self):
        return test_load
