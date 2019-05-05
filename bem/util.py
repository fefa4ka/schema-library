from settings import params_tolerance


def u(unit):
    """Absolute float value of PySpice.Unit
    """
    if type(unit) in [str, int, float]:
        return float(unit)
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
    
