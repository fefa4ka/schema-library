from bem import Build, DEBUG
from PySpice.Unit import u_V, u_ms, u_uF, u_Hz, u_Ohm
from skidl import ERC, generate_netlist

# Template
V_in_value = 10 @ u_V

Power = Build('Power').block
Divider = Build('Divider', type='resistive').block
Decay = Build('Decay', mount='smd').block


# Power Supply
VCC = None
if DEBUG:
    from skidl.pyspice import PULSEV, SINEV, gnd
    # VCC = Power(source=SINEV(amplitude=10@u_V, frequency=100@u_Hz), gnd=gnd)
    VCC = Power(source=PULSEV(initial_value=0, pulsed_value=10 @ u_V, pulse_width=20 @ u_ms, period=40 @ u_ms), gnd=gnd)
else:
    USB = Build('Connector:USB_OTG', footprint='Connector_USB:USB_Mini-B_Lumberg_2486_01_Horizontal').element
    VCC = Power(source=USB)
    PINS = Build('Connector:Conn_01x03_Msale', footprint='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical').element
    gnd = PINS[1]


# Schematics 
divider = Divider(V_in=10 @ u_V, V_out=5 @ u_V)
decay = Decay(V_in=V_in_value, V_out=5 @ u_V, Time_to_V_out=10 @ u_ms, C_out_value=10 @ u_uF)

rc = VCC & divider & decay & gnd


# Deploy
if DEBUG:
    pass
    ERC()
    decay.test()
    divider.test()
else:
    ERC()
    generate_netlist()
