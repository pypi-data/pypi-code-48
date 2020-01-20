#!/usr/bin/env python
# -*- coding: ascii -*-


from rocketcea.cea_obj import CEA_Obj as CEA_Obj_default
from rocketcea.units import get_units_obj

class CEA_Obj( object ):
    """
    RocketCEA wraps the NASA FORTRAN CEA code to calculate Isp, cstar, and Tcomb
    
    This object wraps the English unit version of CEA_Obj to enable desired user units.
    """

    def __init__(self, propName='', oxName='', fuelName='', 
        useFastLookup=0, makeOutput=0, 
        isp='sec', cstar='ft/sec', 
        pressure='psia', temperature='degR', 
        sonic_velocity='ft/sec', enthalpy='BTU/lbm', 
        density='lbm/cuft', specific_heat='BTU/lbm degR'):
            
        # units of input pressures (Pc and Pamb)
        self.pressure       = get_units_obj('psia', pressure )
        
        # units of output quantities
        self.isp            = isp
        self.cstar          = cstar
        self.temperature    = temperature
        self.sonic_velocity = sonic_velocity
        self.enthalpy       = enthalpy
        self.density        = density
        self.specific_heat  = specific_heat
        
        self.cea_obj = CEA_Obj_default(propName=propName, oxName=oxName, fuelName=fuelName, 
                               useFastLookup=useFastLookup, makeOutput=makeOutput)
    
    def get_IvacCstrTc(self, Pc=100.0, MR=1.0, eps=40.0):
        
        Pc = self.pressure.get_dval_from_uval( Pc ) # convert user units to psia
        IspVac, Cstar, Tcomb = self.cea_obj.get_IvacCstrTc( Pc=Pc, MR=MR, eps=eps )
    
    def getFrozen_IvacCstrTc(self, Pc=100.0, MR=1.0, eps=40.0, frozenAtThroat=0):
        pass
        
    def get_IvacCstrTc_exitMwGam(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_IvacCstrTc_ChmMwGam(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_IvacCstrTc_ThtMwGam(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Isp(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Cstar(self, Pc=100.0, MR=1.0):
        pass
        
    def get_Tcomb(self, Pc=100.0, MR=1.0):
        pass
        
    def get_PcOvPe(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_eps_at_PcOvPe(self, Pc=100.0, MR=1.0, PcOvPe=1000.0):
        pass
        
    def get_Throat_PcOvPe(self, Pc=100.0, MR=1.0):
        pass
        
    def get_MachNumber(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_Temperatures(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_SonicVelocities(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_Chamber_SonicVel(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Enthalpies(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_Chamber_H(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Densities(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_Chamber_Density(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_HeatCapacities(self, Pc=100.0, MR=1.0,eps=40.0):
        pass
        
    def get_Chamber_Cp(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Throat_Isp(self, Pc=100.0, MR=1.0):
        pass
        
    def get_Chamber_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_Throat_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_exit_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def get_eqratio(self, Pc=100.0, MR=1.0, eps=40.0):
        pass
        
    def getMRforER(self, ERphi=None, ERr=None):
        pass
        
    def get_description(self):
        pass
        
    def estimate_Ambient_Isp(self, Pc=100.0, MR=1.0, eps=40.0, Pamb=14.7):
        pass
        

if __name__ == "__main__":
    
    C = CEA_Obj(propName='', oxName='N2O4', fuelName="MMH", 
        isp='sec', cstar='ft/sec', 
        pressure='psia', temperature='degR', 
        sonic_velocity='ft/sec', enthalpy='BTU/lbm', 
        density='lbm/cuft', specific_heat='BTU/lbm degR')
        
        
        