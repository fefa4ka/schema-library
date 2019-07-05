from settings import params_tolerance

_prefix = {
    'y': 1e-24,  # yocto
    'z': 1e-21,  # zepto
    'a': 1e-18,  # atto
    'f': 1e-15,  # femto
    'p': 1e-12,  # pico
    'n': 1e-9,   # nano
    'u': 1e-6,   # micro
    'm': 1e-3,   # mili
    'c': 1e-2,   # centi
    'd': 1e-1,   # deci
    'k': 1e3,    # kilo
    'M': 1e6,    # mega
    'G': 1e9,    # giga
    'T': 1e12,   # tera
    'P': 1e15,   # peta
    'E': 1e18,   # exa
    'Z': 1e21,   # zetta
    'Y': 1e24,   # yotta
}

def u(unit):
    """Absolute float value of PySpice.Unit
    """
    if type(unit) in [int, float]:
        return float(unit)
    elif type(unit) == str:
        try:
            return float(unit)
        except:
            return float(unit[:-1]) * _prefix[unit[-1]]
    else:
        return float(unit.convert_to_power())


def label_prepare(text):
    last_dash = text.rfind('_')
    if last_dash > 0:
        text = text[:last_dash] + '$_{' + text[last_dash + 1:] + '}$'

    return text

def is_tolerated(a, b, tollerance=params_tolerance):
    """
    A mathematical model for symmetrical parameter variations is
    `P_(nom) * (1 − ε) ≤ P ≤ P_(nom)(1 + ε)`
    in which `P_(nom)` is the nominal specification for the parameter such as the resistor value or independent source value, and `ε` is the fractional tolerance for the component. 
    
    For example, a resistor `R` with nominal value of 10 kOhm and a 5 percent tolerance could exhibit a resistance anywhere in the following range:
    `10,000 * (1 − 0.05) ≤ R ≤ 10,000 * (1 + 0.05)`
    `9500 ≤ R ≤ 10,500`
    """

    if type(a) == list and b in a:
        return True

    if type(a) not in [int, float]:
        try:
            a = u(a)
        except:
            pass
   
    if type(b) not in [int, float]:
        try:
            b = u(b)
        except:
            pass

    if b == type(b)(a):
        return True

    try:
        b = float(b)
        a = float(a)
        diff = abs(a - b)
        if diff < a * tollerance:
            return True
    except:
        pass
    
    return False
    
