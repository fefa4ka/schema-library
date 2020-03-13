from bem.abstract import Electrical

class Base(Electrical()):
    """
    * TODO: https://www.nutsvolts.com/magazine/article/filter-basics-stop-block-and-rolloff
    * https://www.nutsvolts.com/magazine/article/filter-design-software
    """

    pins = {
        'v_ref': True,
        'input': ('Signal', ['output']),
        'gnd': True
    }

    def willMount(self):
        self.output = self.input

    def circuit(self):
        pass

