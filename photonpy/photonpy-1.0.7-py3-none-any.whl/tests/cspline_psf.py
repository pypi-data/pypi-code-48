
# Steps to run this:
# 
# 1. Download the software from "Real-time 3D single-molecule localization using experimental point spread functions"
#    https://www.nature.com/articles/nmeth.4661#Sec21
# 
# 2. Download the bead calibration stack from 
#    http://bigwww.epfl.ch/smlm/challenge2016/datasets/Tubulin-A647-3D/Data/data.html
# 
# 3. Use above software to generate the cspline calibration .mat file
#    Adjust the path and run this code
#
import numpy as np

from photonpy.smlmlib.context import Context
from photonpy.smlmlib.cspline import CSpline_Calibration, CSpline
import napari



fn = "C:/data/beads/Tubulin-A647-cspline.mat"


with Context() as ctx:
    calib = CSpline_Calibration.from_file_nmeth(fn)
    
    roisize= 16
    psf = CSpline(ctx).CreatePSF_XYZIBg(roisize, calib, False)
    
    N = 200
    theta = np.repeat([[roisize/2,roisize/2,50,1000,3]], N, axis=0)
    theta[:,2]= np.linspace(-1,1,N)
    
    smp = psf.GenerateSample(theta)
    
    with napari.gui_qt():
        napari.view_image(smp)
