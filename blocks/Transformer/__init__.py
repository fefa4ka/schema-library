from bem import Block, Build
from skidl import Part, Net, TEMPLATE, subcircuit
from PySpice.Unit import u_uH, u_mOhm 

class Base(Block):
    increase = False
    
    # def __series__(self, instance):
    #     if self.output and instance.input:
    #         self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
    #         self.output += instance.input
        
    #     if self.output_gnd and instance.gnd:
    #         self.output_gnd += instance.gnd
        
    #     if self.v_ref and instance.v_ref:
    #         self.v_ref += instance.v_ref

    @property
    def spice_part(self):
        #@subcircuit
        def build(V_in=None, V_out=None, N_in=None, N_out=None, L_in=None, L_out=None, turns_ration=None):
            if (not V_in and not V_out) or (not turns_ration and (not V_in or not V_out)):
                raise Exception('Set V_in/V_out/turns_ratio for transformer')

            from skidl.pyspice import K
            L = Build('Inductor').block
            R = Build('Resistor').block
            # C = Build('Capacitor').block

            Transformer = {
                '1': Net('TransformerInputP'),
                '2': Net('TransformerInputN'),
                '3': Net('TransformerOutputP'),
                '4': Net('TransformerOutputN')
            }

            Spacer = R(value=1 @ u_mOhm) 
            Lin = L(value=400 @ u_uH)
            Lout = L(value=39 @ u_uH)
            primary = Transformer['1'] & Spacer & Lin & Transformer['2']
            secondary = Transformer['3'] & Lout & Transformer['4']

            
            transformer = K(ind1=Lin.element, ind2=42342, coupling=0.9)

            return Transformer

        return build        
    

    @property
    def part(self):
        part = Part('Device', 'Transformer_1P_1S', footprint=self.footprint, dest=TEMPLATE)
        
        return part

    def circuit(self, *args, **kwargs):
        BuildBlock = self.spice_part if self.DEBUG else self.part

        transformer = BuildBlock(*args, **kwargs)
        
        instance.input = transformer['1']
        instance.input_n = transformer['2']

        instance.output = transformer['3']
        instance.output_n = transformer['4']

        return instance
