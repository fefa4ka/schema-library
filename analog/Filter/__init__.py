from bem.abstract import Electrical

class Base(Electrical()):
    """
    * TODO: https://www.nutsvolts.com/magazine/article/filter-basics-stop-block-and-rolloff
    * https://www.nutsvolts.com/magazine/article/filter-design-software
    ```
    vs = VS(flow='SINEV')(V=5, frequency=[1e3, 1e6])
    load = Resistor()(1000)
    filter = Example()
    vs & filter & load & vs

    watch = filter
    ```
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

