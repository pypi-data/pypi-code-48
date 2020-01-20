import numpy as np
from scipy.linalg import eig # NOT SURE WHY NUMPY ONE SEG FAULTS

def main_direction(X):
    v,_ = eig(X)
    v = np.real(v) # NOTE: NOT SURE WHY THIS IS NECESSARY
    # idx=np.argmax(V)
    # print(v))
    angle=np.arctan2(v[1],v[0]) # HACK: CHECK THIS!!!!!
    if (angle < 0): angle=angle + np.pi
    elif (angle > np.pi): angle=angle - np.pi
    dzeta=np.sqrt(np.sum(X ** 2))
    return angle, dzeta

def window_mask(patchw=32):
    # Window mask definition: compute a radial hanning window
    w = np.zeros([patchw*2,patchw*2])
    for i in range(1,patchw * 2):
        for j in range(1,patchw * 2):
            dst=np.sqrt((i - 0.5 - patchw) ** 2 + (j - 0.5 - patchw) ** 2)
            w[i,j]=0.5 * (np.cos(2 * np.pi * dst / (patchw * 2))) + 0.5
            if (dst > patchw):
                w[i,j]=0
    return w

def angular_binning(patchw=32,N=10000):
    # Angular binning definition
    # step_angle=5 / 180 * pi
    # bin_angle=range(0 - step_angle / 2,- 180,- step_angle)
    # n_angle=floor(pi / step_angle)

    # Monte-Carlo method to compute the individual Q(k) coefficients for equation 4.
    # n_maskQ is a 4D table such as Q(kx, ky)=n_maskQ(kx,ky,:,:)
    # N is Number of particle throw per iteration (10000 gives a smooth result)
    K = np.zeros([N,2])
    n_nbmaskQ = np.zeros([patchw * 2,patchw * 2])
    n_maskQ   = np.zeros([patchw * 2,patchw * 2,2,2])
    for j in range(1,1000): # Number of iteration in Monte-Carlo simulation
        r = (np.random.rand(N,2) - 0.5) * 2 * patchw
        K[:,0] = r[:,0] / (np.sqrt(r[:,0] ** 2 + r[:,1] ** 2))
        K[:,1] = r[:,1] / (np.sqrt(r[:,0] ** 2 + r[:,1] ** 2))
        x = np.floor(r + patchw)
        x = x.astype(np.int)
        for i in range(1,N):
            n_nbmaskQ[x[i,1],x[i,0]] += 1
            n_maskQ[x[i,1],x[i,0],0,0] += K[i,0] * K[i,0]
            n_maskQ[x[i,1],x[i,0],0,1] += K[i,0] * K[i,1]
            n_maskQ[x[i,1],x[i,0],1,0] += K[i,1] * K[i,0]
            n_maskQ[x[i,1],x[i,0],1,1] += K[i,1] * K[i,1]

    # Final scaling for the n_maskQ coefficients.
    n_maskQ[:,:,0,0] /= n_nbmaskQ
    n_maskQ[:,:,0,1] /= n_nbmaskQ
    n_maskQ[:,:,1,0] /= n_nbmaskQ
    n_maskQ[:,:,1,1] /= n_nbmaskQ

    return n_maskQ

def orientation_map(data,start=0,end=None,xstep=32,ystep=32,patchw=32):
    w = window_mask(patchw)
    n_maskQ = angular_binning(patchw,N=100) # NOTE: LOW N FOR TESTING - REMOVE THIS LATER

    nt,nx,ny = data.shape

    gridx = range(patchw,nx-patchw,xstep) # locations of centres of patches in x direction
    gridy = range(patchw,ny-patchw,ystep) # locations of centres of patches in y direction
    if end is None: end = nt # optionally set end time

    # Prepare thre result matrices (3D), first 2 indices are the grid, the last index is time
    orient = np.nan * np.zeros([len(gridx),len(gridy),end-start])
    dzeta  = np.nan * np.zeros([len(gridx),len(gridy),end-start])
    Q = np.zeros_like(n_maskQ)
    Q2 = np.zeros([2,2,nx,ny,nt])

    for t,ti in enumerate(range(start,end)): # Loop on the movie frames
        for i,xi in enumerate(gridx): # Loop over the grid
            for j,yj in enumerate(gridy):
                patch = data[ti,xi-patchw:xi+patchw,yj-patchw:yj+patchw]

                if np.std(patch) != 0: patch=(patch - np.mean(patch)) / np.std(patch)
                else:                  patch=(patch - np.mean(patch))

                S = np.fft.fftshift(np.abs(np.fft.fft2(patch*w) ** 2))

                if np.sum(S) == 0:
                    Q[:,:,0,0] = S
                    Q[:,:,0,1] = S
                    Q[:,:,1,0] = S
                    Q[:,:,1,1] = S
                else:
                    Q[:,:,0,0] = n_maskQ[:,:,0,0].dot(S) / np.sum(np.sum(S))
                    Q[:,:,0,1] = n_maskQ[:,:,0,1].dot(S) / np.sum(np.sum(S))
                    Q[:,:,1,0] = n_maskQ[:,:,1,0].dot(S) / np.sum(np.sum(S))
                    Q[:,:,1,1] = n_maskQ[:,:,1,1].dot(S) / np.sum(np.sum(S))
                # Q2[:,:,j,i,t] = np.transpose(np.sum(np.sum(Q,0),1), axes=[2,3,0,1])
                Q2[:,:,i,j,t] = np.sum(np.sum(Q,0),0)
                Q2[0,0,i,j,t] -= 0.5
                Q2[1,1,i,j,t] -= 0.5
                Q2[:,:,i,j,t] *= np.sqrt(2)
                orient[i,j,t],dzeta[i,j,t] = main_direction(Q2[:,:,i,j,t])
    return orient, dzeta

# Testing area
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # w = window_mask()
    # plt.imshow(w)
    # plt.colorbar()
    # plt.show()

    # n_maskQ = angular_binning(N=1000)
    # plt.subplot(221)
    # plt.imshow(n_maskQ[:,:,0,0])
    # plt.colorbar()
    # plt.subplot(222)
    # plt.imshow(n_maskQ[:,:,0,1])
    # plt.colorbar()
    # plt.subplot(223)
    # plt.imshow(n_maskQ[:,:,1,0])
    # plt.colorbar()
    # plt.subplot(224)
    # plt.imshow(n_maskQ[:,:,1,1])
    # plt.colorbar()
    # plt.show()

    # m = np.array([[1,0],[1,0]])
    # angle,dzeta = main_direction(m)
    # print(np.degrees(angle),dzeta)
    # m = np.array([[1,0],[0,1]])
    # angle,dzeta = main_direction(m)
    # print(np.degrees(angle),dzeta)
    # m = np.array([[0,1],[1,0]])
    # angle,dzeta = main_direction(m)
    # print(np.degrees(angle),dzeta)

    from pynamix.data import radiographs
    data,logfile = radiographs()
    orient, dzeta = orientation_map(data,start=1000,end=1002)

    plt.subplot(121)
    plt.imshow(data[1000])
    plt.subplot(122)
    plt.pcolormesh(orient[:,:,0])
    plt.colorbar()
    plt.show()
