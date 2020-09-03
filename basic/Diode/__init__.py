from bem import Build, u_V, u_A, u_S
from bem.abstract import Physical
from skidl import Part, TEMPLATE


class Base(Physical()):
    """
    # Diode

    A diode is a two-terminal electronic component that conducts current primarily in one direction (asymmetric conductance); it has low (ideally zero) resistance in one direction, and high (ideally infinite) resistance in the other.

    The most common function of a diode is to allow an electric current to pass in one direction (called the diode's forward direction), while blocking it in the opposite direction (the reverse direction). As such, the diode can be viewed as an electronic version of a check valve. This unidirectional behavior is called rectification, and is used to convert alternating current (ac) to direct current (dc). Forms of rectifiers, diodes can be used for such tasks as extracting modulation from radio signals in radio receivers.

    However, diodes can have more complicated behavior than this simple on–off action, because of their nonlinear current-voltage characteristics. Semiconductor diodes begin conducting electricity only if a certain threshold voltage or cut-in voltage is present in the forward direction (a state in which the diode is said to be forward-biased). 

    ## Forward Current Versus Forward Voltage
    The voltage drop across a forward-biased diode varies only a little with the current, and is a function of temperature; this effect can be used as a temperature sensor or as a voltage reference. 
    ```
    vs = VS(flow='V')(V=slice(0, 0.2, .01))
    load = Resistor()(1000)
    diode = Example()
    vs & diode & load & vs

    watch = diode
    ```

    ## Reverse Current Versus Reverse Voltage
    Also, diodes' high resistance to current flowing in the reverse direction suddenly drops to a low resistance when the reverse voltage across the diode reaches a value called the breakdown voltage.

    ```
    vs = VS(flow='V')(V=slice(-0.3, 0.1, .01))
    load = Resistor()(1000)
    diode = Example()
    vs & diode & load & vs

    watch = diode
    ```

    """

    spice_params = {
        'AF': {'description': 'Flicker noise exponent', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'BV': {'description': 'Reverse breakdown voltage', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'CJO': {'description': 'Zero-bias junction capacitance', 'unit': { 'suffix': 'F', 'name': 'farad' }, 'value': ''},
        'EG': {'description': 'Band-gap energy', 'unit': { 'suffix': 'eV', 'name': 'electron volt' }, 'value': ''},
        'FC': {'description': 'Coefficient for forward-bias', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'IBV': {'description': 'Current at breakdown voltage', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'IS': {'description': 'Saturation current', 'unit': { 'suffix': 'A', 'name': 'ampere' }, 'value': ''},
        'KF': {'description': 'Flicker noise coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'M': {'description': 'Grading coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'N': {'description': 'Emission coefficient', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''},
        'RS': {'description': 'Ohmic resistanc', 'unit': { 'suffix': 'Ω', 'name': 'ohm' }, 'value': ''},
        'TNOM': {'description': 'Parameter measurement temperature', 'unit': { 'suffix': '°', 'name': 'degree' }, 'value': ''},
        'TT': {'description': 'Transit-time', 'unit': { 'suffix': 's', 'name': 'sec' }, 'value': ''},
        'VJ': {'description': 'Junction potential', 'unit': { 'suffix': 'V', 'name': 'volt' }, 'value': ''},
        'XTI': {'description': 'Saturation-current temp.exp', 'unit': { 'suffix': '', 'name': 'number' }, 'value': ''}
    }

    def willMount(self):
        """
        V_j -- Junction potential
        V_drop -- Voltage drop
        """

        self.Power = self.I_load

    def circuit(self):
        # Тесты хуесты
        self.V_j = (self['VJ'] or 0.6) @ u_V

        self.consumption(self.V_j)
        self.load(self.V - self.V_j)

        super().circuit()

    def part_spice(self, *args, **kwargs):
        return Build('D').spice(*args, **kwargs)

    def part(self):
        part = super().part(model=self.model)
        if not part['A']:
            part.set_pin_alias('A', 1)

        if not part['K']:
            part.set_pin_alias('K', 2)


        return part

