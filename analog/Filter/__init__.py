from bem.abstract import Electrical

class Base(Electrical()):
    """
    # Filter
    Some filters made from resistors and capacitors.
    Those simple RC filters produced gentle highpass or lowpass gain characteristics,
    with a 6 dB/octave falloff well beyond the −3 dB point. By cascading highpass
    and lowpass filters, we showed how to ob- tain bandpass filters,
    again with gentle 6 dB/octave “skirts.” Such filters are sufficient for many purposes,
    especially if the signal being rejected by the filter is far removed in frequency from the
    desired signal passband.

    Some examples are bypassing of radiofrequency signals in audio circuits, “blocking” capacitors
    for elimination of dc levels, and separation of modulation from a communications “carrier.”


    * Paul Horowitz and Winfield Hill. "6.2 Passive filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 391
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

