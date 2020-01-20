#!/usr/bin/env python
# -*- coding: ascii -*-

"""
This file wraps default RockeCEA units with desired user units.
"""
import sys
from future.utils import raise_

# build a dictionary of conversion factors
unitsConvFactD = {} # index=default units: value=dictionary of conversion factor data
#          for default dictionaries index=new units: value=(multiplier, offset)

# ----------- set up master dictionary for conversion factors --------------
def add_default_unit( name='psia', akaL=None ):
    """Initialize unitsConvFactD for various default units."""
    unitsConvFactD[ name ] = {}
    unitsConvFactD[ name ][ name ] = (1.0, 0)
    # allow user to call them out with all upper or lower case
    unitsConvFactD[ name ][ name.lower() ] = (1.0, 0)
    unitsConvFactD[ name ][ name.upper() ] = (1.0, 0)
    
    if akaL is not None:
        for aka in akaL:
            unitsConvFactD[ name ][ aka ] = (1.0, 0)
            # allow user to call them out with all upper or lower case
            unitsConvFactD[ name ][ aka.lower() ] = (1.0, 0)
            unitsConvFactD[ name ][ aka.upper() ] = (1.0, 0)

# the following are the default units for i/o of RockeCEA
add_default_unit( 'psia' )
add_default_unit( 'degR', ['R'] )
add_default_unit( 'ft/sec', ['fps'] )
add_default_unit( 'lbf sec/lbm', ['sec', 'lbf-sec/lbm'] )
add_default_unit( 'BTU/lbm' )
add_default_unit( 'lbm/cuft' )
add_default_unit( 'BTU/lbm degR', ['BTU/lbm-degR','BTU/lbm R','BTU/lbm-R'] )

# ----------- function to get new units conversion factor --------------
def get_conv_factor( default_units, user_units ):
    """Get multiplier and offset for user_units."""
    D = unitsConvFactD[ default_units ]
    
    (uod, offset) = D.get(user_units, (None,None))
    if uod is None:
        traceback = sys.exc_info()[2]
        raise_( ValueError, 'units "%s" not recognized'%user_units, traceback )
            
    return uod, offset # multiplier is (user_units / default_units)

# ----------- function to add new units to master dictionary --------------
def add_user_units( default_units, user_units, multiplier, offset=0 ):
    """Add new units to dictionary of default_units."""
    # get dictionary for default_units
    D = unitsConvFactD[ default_units ]
    D[ user_units ] = (multiplier, offset)
    
    # allow user to call them out with all upper or lower case
    D[ user_units.lower() ] = (multiplier, offset)
    D[ user_units.upper() ] = (multiplier, offset)
    
# ----------- add units for Pressure --------------
add_user_units('psia', 'MPa', 0.00689475729)
add_user_units('psia', 'kPa', 6.89475729)
add_user_units('psia', 'Bar', 0.0689475729)
add_user_units('psia', 'Atm', 0.068046)
add_user_units('psia', 'Torr', 51.7149)

add_user_units('degR', 'degK', 5.0/9.0)
add_user_units('degR', 'K', 5.0/9.0)
add_user_units('degR', 'degC', 5.0/9.0 , -273.15)
add_user_units('degR', 'C', 5.0/9.0 , -273.15)
add_user_units('degR', 'degF', 1.0 , -459.67)
add_user_units('degR', 'F', 1.0 , -459.67)

class Units( object ):
    
    def __init__(self, default_units='psia', user_units='MPa', 
                 user_over_default=0.0068947572, user_offset=0):
        """
        default = string defining default units in RockeCEA
        user    = string defining desired user units
        user_over_default = conversion factor to user units from default units.
        user_offset       = additive offset from simple conversion (Temperature only)
        """
        
        self.default_units     = default_units
        self.user_units        = user_units
        self.user_over_default = user_over_default
        
        if user_offset is None:
            user_offset = 0
        self.user_offset       = user_offset # only used for temperature and psig

    def __str__(self):
        if self.user_offset:
            if self.user_offset > 0:
                s = '+ %g'%self.user_offset
            else:
                s = '- %g'%abs(self.user_offset)
            return 'User units:"%s" = %g * "%s" %s'%(self.user_units, 
                   self.user_over_default, self.default_units, s )
        else:
            return 'User units:"%s" = %g * "%s"'%(self.user_units, 
                   self.user_over_default, self.default_units)

    def __call__(self, user_value): # same as: get_dval_from_uval
        """Given a value in user units, return RockeCEA default value"""
        return self.get_dval_from_uval( user_value )

    def get_dval_from_uval(self, user_value):
        """Given a value in user units, return a value in RockeCEA default units."""
        return (user_value-self.user_offset) / self.user_over_default

    def get_uval_from_dval(self, def_value):
        """Given a value in RockeCEA default units, return value in user units."""
        return def_value * self.user_over_default + self.user_offset

    def show_uval_from_dval(self, def_value):
        """Given a value in RockeCEA default units, print conversion user units."""
        user_value = self.get_uval_from_dval( def_value )
        print( '%g %s = %g %s'%(def_value, self.default_units, user_value, self.user_units) )

    def show_dval_from_uval(self, user_value):
        """Given a value in user units, print conversion to RockeCEA default units."""
        def_value = self( user_value )
        print( '%g %s = %g %s'%( user_value, self.user_units, def_value, self.default_units) )

# ======================= Factory function for Units objects ==============
def get_units_obj( default_units, user_units ):
    
        uod, offset = get_conv_factor( default_units, user_units )
                
        return Units( default_units=default_units, user_units=user_units, 
                      user_over_default=uod, user_offset=offset )
    

if __name__ == "__main__":
    
    def chk_obj( U, user_val=1.0 ):
        print('*'*44)
        dv = U.get_dval_from_uval( user_val )
        uvcalc = U.get_uval_from_dval( dv )
        print( U, '\n%g %s = %g %s'%(user_val,U.user_units, dv, U.default_units),
                  '==> %g %s = %g %s'%(dv, U.default_units, uvcalc, U.user_units) )
        
    
    P = Units(default_units='psia', user_units='MPa', user_over_default=0.0068947572)
    chk_obj( P )
    
    chk_obj( Units(default_units='degR', user_units='degC', user_over_default=5.0/9.0, 
             user_offset=-273.15) )
        
    chk_obj( get_units_obj('psia', 'MPa') )
    chk_obj( get_units_obj('psia', 'bar') )
    chk_obj( get_units_obj('psia', 'ATM') )
    
    chk_obj( get_units_obj('degR', 'K') )
    chk_obj( get_units_obj('degR', 'c') )
    chk_obj( get_units_obj('degR', 'degf') )
    