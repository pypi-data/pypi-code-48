"""Python package ismember returns array elements that are members of set array.

  from ismember import ismember
  [Lia,Locb]= ismember(list1, list2)

 
 Example
 -------
    import numpy as np
    from ismember import ismember

    a_vec  = [1,2,3,None]
    b_vec  = [4,1,2]
    [I,idx] = ismember(a_vec,b_vec)
    np.array(a_vec)[I]
    np.array(b_vec)[idx]

    a_vec   = pd.DataFrame(['aap','None','mies','aap','boom','mies',None,'mies','mies','pies',None])
    b_vec   = pd.DataFrame([None,'mies','mies','pies',None])
    [I,idx] = ismember(a_vec,b_vec)
    a_vec.values[I]
    b_vec.values[idx]

    a_vec   = np.array([1,2,3,None])
    b_vec   = np.array([1,2,4])
    [I,idx] = ismember(a_vec,b_vec)
    a_vec[I]
    b_vec[idx]

    a_vec   = np.array(['boom','aap','mies','aap'])
    b_vec   = np.array(['aap','boom','aap'])
    [I,idx] = ismember(a_vec,b_vec)
    a_vec[I]
    b_vec[idx]


"""

# --------------------------------------------------------------------------
# Name        : ismember.py
# Author      : E.Taskesen
# Contact     : erdogan@gmail.com
# Licence     : MIT
# --------------------------------------------------------------------------

#%% Libraries
import numpy as np

# %% Main
def ismember(a_vec, b_vec):
    """
    
    Description
    -----------
    MATLAB equivalent ismember function
    [LIA,LOCB] = ISMEMBER(A,B) also returns an array LOCB containing the
    lowest absolute index in B for each element in A which is a member of
    B and 0 if there is no such index.


    Parameters
    ----------
    a_vec : list or array
    b_vec : list or array

    Returns an array containing logical 1 (true) where the data in A is found 
    in B. Elsewhere, the array contains logical 0 (false)
    -------
    Tuple

    """
    I   = []
    idx = []

    # Check type
    if 'pandas' in str(type(a_vec)):
         a_vec.values[np.where(a_vec.values==None)]='NaN'
         a_vec = np.array(a_vec.values)
    if 'pandas' in str(type(b_vec)):
         b_vec.values[np.where(b_vec.values==None)]='NaN'
         b_vec = np.array(b_vec.values)
    if isinstance(a_vec, list):
        a_vec=np.array(a_vec)
        # a_vec[a_vec==None]='NaN'
    if isinstance(b_vec, list):
        b_vec=np.array(b_vec)
        # b_vec[b_vec==None]='NaN'
    
    bool_ind = np.isin(a_vec,b_vec)
    common = a_vec[bool_ind]
    [common_unique, common_inv]  = np.unique(common, return_inverse=True)
    [b_unique, b_ind] = np.unique(b_vec, return_index=True)
    common_ind = b_ind[np.isin(b_unique, common_unique, assume_unique=True)]

    I=bool_ind
    idx=common_ind[common_inv]

    return(I,idx)    