import numpy as np
from numpy import concatenate as cat
from matlab_functions import ismember
from scipy.linalg import toeplitz
from SurfStatEdg import py_SurfStatEdg

def pacos(x):
    return np.arccos( np.minimum(np.abs(x),1) * np.sign(x) ) 

def py_SurfStatResels(slm, mask=None):
    if 'tri' in slm:
        # Get unique edges. Subtract 1 from edges to conform to Python's counting from 0 - RV
        tri = np.sort(slm['tri']) - 1
        edg = np.unique(np.vstack((tri[:,(0,1)], tri[:,(0,2)], tri[:,(1,2)])),axis=0)

        # If no mask is provided, create one with all included vertices set to 1. - RV
        # If one is provided, simply grab the number of vertices from the mask. - RV  
        if mask is None:
            v = np.amax(edg)+1
            mask = np.full(v,False)
            mask[edg-1] = True
        else:
            #if np.ndim(mask) > 1:
                #mask = np.squeeze(mask)
                #if mask.shape[0] > 1:
                #    mask = mask.T
            v = mask.size
        
        ## Compute the Lipschitz–Killing curvatures (LKC) - RV
        m = np.sum(mask)
        if 'resl' in slm:
            lkc = np.zeros((3,3))
        else:
            lkc = np.zeros((1,3))
        lkc[0,0] = m

        # LKC of edges
        maskedg = np.all(mask[edg],axis=1)
        lkc[0,1] = np.sum(maskedg)
        if 'resl' in slm:
            r1 = np.mean(np.sqrt(slm['resl'][maskedg,:]),axis=1)
            lkc[1,1] = np.sum(r1)
        
        # LKC of triangles
        # Made an adjustment from the MATLAB implementation: 
        # The reselspvert computation is included in the if-statement. 
        # MATLAB errors when the if statement is false as variable r2 is not
        # defined during the computation of reselspvert. - RV
        masktri = np.all(mask[tri],1)
        lkc[0,2] = np.sum(masktri)
        if 'resl' in slm:
            _, loc = ismember(tri[masktri,:][:,[0,1]], edg, 'rows')
            l12 = slm['resl'][loc,:]
            _, loc = ismember(tri[masktri,:][:,[0,2]], edg, 'rows')
            l13 = slm['resl'][loc,:]
            _, loc = ismember(tri[masktri,:][:,[1,2]], edg, 'rows')
            l23 = slm['resl'][loc,:]
            a = np.maximum(4*l12*l13-(l12+l13-l23)**2,0)
            r2 = np.mean(np.sqrt(a),axis=1)/4
            lkc[1,2] = np.sum(np.mean(np.sqrt(l12)+np.sqrt(l13)+np.sqrt(l23),axis=1))/2
            lkc[2,2] = np.sum(r2,axis=0)
        
            # Compute resels per mask vertex
            reselspvert = np.zeros(v)
            for j in range(0,3):
                reselspvert = reselspvert + np.bincount(tri[masktri,j],weights=r2,minlength=v)
            D = 2
            reselspvert = reselspvert.T / (D+1) / np.sqrt(4*np.log(2)) ** D
        else:
            reselspvert = None
        
    if 'lat' in slm:
        edg = py_SurfStatEdg(slm)
        # The lattice is filled with 5 alternating tetrahedra per cube
        I, J, K = np.shape(slm['lat'])
        IJ = I*J
        i, j = np.meshgrid(range(1,I+1),range(1,J+1))
        i = np.squeeze(np.reshape(i,(-1,1)))
        j = np.squeeze(np.reshape(j,(-1,1)))
        
        c1  = np.argwhere(((i+j)%2)==0 & (i < I) & (j < J))
        c2  = np.argwhere(((i+j)%2)==0 & (i > 1) & (j < J))
        c11 = np.argwhere(((i+j)%2)==0 & (i == I) & (j < J))
        c21 = np.argwhere(((i+j)%2)==0 & (i == I) & (j > 1))
        c12 = np.argwhere(((i+j)%2)==0 & (i < I) & (j == J))
        c22 = np.argwhere(((i+j)%2)==0 & (i > 1) & (j == J))

        d1  = np.argwhere(((i+j)%2)==0 & (i < I) & (j < J))+IJ
        d2  = np.argwhere(((i+j)%2)==0 & (i > 1) & (j < J))+IJ

        tri1 = cat((
            cat((c1, c1+1, c1+1+I),axis=1),
            cat((c1, c1+I, c1+1+I),axis=1),
            cat((c2-1, c2, c2-1+I),axis=1),
            cat((c2, c2-1+I, c2+I),axis=1)),
            axis=0)
        tri2= cat((
            cat((c1,    c1+1,    c1+1+IJ),axis=1),
            cat((c1,    c1+IJ,   c1+1+IJ),axis=1),
            cat((c1,    c1+I,    c1+I+IJ),axis=1),
            cat((c1,     c1+IJ,   c1+I+IJ),axis=1),
            cat((c1,     c1+1+I,  c1+1+IJ),axis=1),
            cat((c1,     c1+1+I,  c1+I+IJ),axis=1),
            cat((c1,     c1+1+IJ, c1+I+IJ),axis=1),
            cat((c1+1+I, c1+1+IJ, c1+I+IJ),axis=1),
            cat((c2-1,   c2,      c2-1+IJ),axis=1),
            cat((c2,     c2-1+IJ, c2+IJ),axis=1),
            cat((c2-1,   c2-1+I,  c2-1+IJ),axis=1),
            cat((c2-1+I, c2-1+IJ, c2-1+I+IJ),axis=1),
            cat((c2,     c2-1+I,  c2+I+IJ),axis=1),
            cat((c2,     c2-1+IJ, c2+I+IJ),axis=1),
            cat((c2,     c2-1+I,  c2-1+IJ),axis=1),
            cat((c2-1+I, c2-1+IJ, c2+I+IJ),axis=1),
            cat((c11,    c11+I,    c11+I+IJ),axis=1),
            cat((c11,    c11+IJ,   c11+I+IJ),axis=1),
            cat((c21-I,  c21,      c21-I+IJ),axis=1),
            cat((c21,    c21-I+IJ, c21+IJ),axis=1),
            cat((c12,    c12+1,    c12+1+IJ),axis=1),
            cat((c12,    c12+IJ,   c12+1+IJ),axis=1),
            cat((c22-1,  c22,      c22-1+IJ),axis=1),
            cat((c22,    c22-1+IJ, c22+IJ),axis=1)),
            axis=0)
        tri3 = cat((
            cat((d1,     d1+1,    d1+1+I),axis=1), 
            cat((d1,     d1+I,    d1+1+I),axis=1),
            cat((d2-1,   d2,      d2-1+I),axis=1),
            cat((d2,     d2-1+I,  d2+I),axis=1)),
            axis=0)
        tet1 = cat((
            cat((c1,     c1+1,    c1+1+I,    c1+1+IJ),axis=1), 
            cat((c1,     c1+I,    c1+1+I,    c1+I+IJ),axis=1),
            cat((c1,     c1+1+I,  c1+1+IJ,   c1+I+IJ),axis=1),
            cat((c1,     c1+IJ,   c1+1+IJ,   c1+I+IJ),axis=1),
            cat((c1+1+I, c1+1+IJ, c1+I+IJ,   c1+1+I+IJ),axis=1),
            cat((c2-1,   c2,      c2-1+I,    c2-1+IJ),axis=1),
            cat((c2,     c2-1+I,  c2+I,      c2+I+IJ),axis=1),
            cat((c2,     c2-1+I,  c2-1+IJ,   c2+I+IJ),axis=1),
            cat((c2,     c2-1+IJ, c2+IJ,     c2+I+IJ),axis=1),
            cat((c2-1+I, c2-1+IJ, c2-1+I+IJ, c2+I+IJ),axis=1)),
            axis=0)
        
        v = np.int(np.round(np.sum(slm['lat'])))
        if mask is None:
            mask = np.ones((1,v))
        
        reselspvert = np.zeros(v)
        vs = np.cumsum(np.squeeze(np.sum(np.sum(slm['lat'],axis=0),axis=1)))
        vs = cat((np.zeros(1),vs,np.expand_dims(vs[K-1],axis=0)),axis=0)
        es = 0 
        lat = np.zeros((I,J,2))
        lat[:,:,0] = slm['lat'][:,:,0]
        lkc = np.zeros((4,4))
        n10 = np.floor(K/10)
        for k in range(0,K):
            f = k % 2
            if k < (K-1):
                lat[:,:,f+1] = slm['lat'][:,:,k+1]
            else:
                lat[:,:,f+1] = np.zeros((I,J))
            vid = (np.cumsum(lat) * np.reshape(lat.T,-1)).astype(int)
            if f:
                edg1 = edg[edg[:,0] > vs[k] & edg[:,0] <= vs[k+1],:]-vs[k] # Indexing may go wrong here.
                edg2 = edg[edg[:,0] > vs[k] & edg[:,1] <= vs[k+2],:]-vs[k]
                tri = cat((vid[tri1[np.all(lat[tri1],1),:]], 
                                    vid[tri2[np.all(lat[tri2],1),:]]),
                                    axis=0)
                mask1 = mask[np.arange(vs[k]+1,vs[k+2])]
            else:
                edg1 = cat((
                    edg[edg[:,0]  > vs[k]   & edg[:,1] <= vs[k+1], :] - vs[k] + vs[k+2] - vs[k+1],
                    edg[edg[:,0] <= vs[k+1] & edg[:,1] >  vs[k+1], 1] - vs[k+1],
                    edg[edg[:,0] <= vs[k+1] & edg[:,1] >  vs[k+1], 0] - vs[k] + vs[k+2] - vs[k+1]),
                    axis=0)
                edg2 = cat((
                    edg1, 
                    edg[edg[:,0] > vs[k+1] & edg[:,1] <= vs[k+2],:] - vs[k+1]),
                    axis=0)
                tri = cat((
                    vid[tri3[np.all(lat[tri3],axis=1),:]],
                    vid[tri2[np.all(lat[tri2],axis=1),:]]),
                    axis=0)
                mask1 = cat((
                    mask[np.arange(mask[vs[k+1]+1], vs[k+2]+1)],
                    mask[np.arange(mask[vs[k]+1],   vs[k+1]+1)]))
            tet = vid[tet1[np.all(lat[tet1],axis=1),:]]

            m1 = np.max(float(edg2[:,0]))
            ue = float(edg2[:,0]) + m1 * (float(edg2[:,1])-1)
            e = edg2.shape[0]
            ae = np.arange(1,e+1)
            if e < 2 ** 31:
                sparsedg = sparse(ae,(ue,1))
            ##
            lkc1 = np.zeros(4,4)
            lkc[0,0] = np.sum(mask[np.arange(vs[k]+1,vs[k+1]+1)])

            ## LKC of edges
            maskedg = np.all(mask1[edg1],axis=1)
            lkc[0,1] = np.sum(maskedg)
            if 'resl' in slm:
                r1 = np.mean(np.sqrt(slm['resl'][np.argwhere(maskedg)+es,:]),axis=1)
                lkc1[1,1] = np.sum(r1)
            
            ## LKC of triangles
            masktri = np.all(mask1[tri],axis=1)
            lkc1[0,2] = np.sum(masktri)
            if 'resl' in slm: 
                if e < 2 ** 31:
                    l12 = slm['resl'][sparsedg[tri[masktri,0] + m1 * (tri[masktri,1]-1), 0] + es, :]
                    l13 = slm['resl'][sparsedg[tri[masktri,0] + m1 * (tri[masktri,2]-1), 0] + es, :]
                    l23 = slm['resl'][sparsedg[tri[masktri,1] + m1 * (tri[masktri,2]-1), 0] + es, :]
                else:
                    l12 = slm['resl'][interp1(ue,ae,tri[masktri,0] + m1 * (tri[masktri,1] - 1),kind='nearest') + es, :]
                    l13 = slm['resl'][interp1(ue,ae,tri[masktri,0] + m1 * (tri[masktri,2] - 1),kind='nearest') + es, :]
                    l23 = slm['resl'][interp1(ue,ae,tri[masktri,1] + m1 * (tri[masktri,2] - 1),kind='nearest') + es, :]
                a = np.maximum(4 * l12 * l13 - (l12+l13-l23) ** 2, 0)
                r2 = np.mean(np.sqrt(a),axis=1)/4
                lkc1[1,2] = np.sum(np.mean(np.sqrt(l12)+np.sqrt(l13)+np.sqrt(l23),axis=1))/2
                lkc1[2,2] = np.sum(r2)

                # The following if-statement has nargout >=2 in MATLAB, but there's no Python equivalent so ignore that. - RV
                if K == 1:
                    for j in range(0,3):
                        if f:
                            v1 = tri[masktri,j] + vs[k]
                        else:
                            v1 = tri[masktri,j] + vs[k+1]
                            v1 = v1 - int(vs > vs[k+2]) * (vs[k+2]-vs[k])
                        reselspvert = reselspvert + accum(v1,r2, size=[v, 1])

            ## LKC of tetrahedra
            masktet = np.all(mask1[tet],axis=1)
            lkc1[1,4] = np.sum(masktet)
            if 'resl' in slm and k < K:
                if e < 2 ** 31:
                    l12 = slm['resl'][sparsedg[tet[masktet,0] + m1 * (tet[masktet,1]-1),0] + es, :]
                    l13 = slm['resl'][sparsedg[tet[masktet,0] + m1 * (tet[masktet,2]-1),0] + es, :]
                    l23 = slm['resl'][sparsedg[tet[masktet,1] + m1 * (tet[masktet,2]-1),0] + es, :]
                    l14 = slm['resl'][sparsedg[tet[masktet,0] + m1 * (tet[masktet,3]-1),0] + es, :]
                    l24 = slm['resl'][sparsedg[tet[masktet,1] + m1 * (tet[masktet,3]-1),0] + es, :]
                    l34 = slm['resl'][sparsedg[tet[masktet,2] + m1 * (tet[masktet,3]-1),0] + es, :]
                else:
                    l12 = slm['resl'][interp1(ue,ae,tet[masktet,0]+m1*(tet[masktet,1]-1),kind='nearest')+es,:]
                    l13 = slm['resl'][interp1(ue,ae,tet[masktet,0]+m1*(tet[masktet,2]-1),kind='nearest')+es,:]
                    l23 = slm['resl'][interp1(ue,ae,tet[masktet,1]+m1*(tet[masktet,2]-1),kind='nearest')+es,:]
                    l14 = slm['resl'][interp1(ue,ae,tet[masktet,0]+m1*(tet[masktet,3]-1),kind='nearest')+es,:]
                    l24 = slm['resl'][interp1(ue,ae,tet[masktet,1]+m1*(tet[masktet,3]-1),kind='nearest')+es,:]
                    l34 = slm['resl'][interp1(ue,ae,tet[masktet,2]+m1*(tet[masktet,3]-1),kind='nearest')+es,:]
                a4 = np.maximum(4 * l12 * l13 - (l12 + l13 -l23) ** 2, 0)
                a3 = np.maximum(4 * l12 * l14 - (l12 + l14 -l24) ** 2, 0)
                a2 = np.maximum(4 * l13 * l14 - (l13 + l14 -l34) ** 2, 0)   
                a1 = np.maximum(4 * l23 * l24 - (l23 + l24 -l34) ** 2, 0)    

                d12 = 4 * l12 * l34 - (l13 + l24 - l23 - l14) ** 2
                d13 = 4 * l13 * l24 - (l12 + l34 - l23 - l14) ** 2
                d14 = 4 * l14 * l23 - (l12 + l34 - l24 - l13) ** 2

                h = np.logical_or(a1 <= 0, a2 <= 0)
                delta12 = np.sum(np.mean(np.sqrt(l34) * pacos((d12-a1-a2) / np.sqrt(a1 * a2 + h) / 2 * (1-h) + h),axis=1))
                h = np.logical_or(a1 <= 0, a3 <= 0)
                delta13 = np.sum(np.mean(np.sqrt(l24) * pacos((d13-a1-a3) / np.sqrt(a1 * a3 + h) / 2 * (1-h) + h),axis=1))
                h = np.logical_or(a1 <= 0, a4 <= 0)
                delta14 = np.sum(np.mean(np.sqrt(l23) * pacos((d14-a1-a4) / np.sqrt(a1 * a4 + h) / 2 * (1-h) + h),axis=1))
                h = np.logical_or(a2 <= 0, a3 <= 0)
                delta23 = np.sum(np.mean(np.sqrt(l14) * pacos((d14-a2-a3) / np.sqrt(a2 * a3 + h) / 2 * (1-h) + h),axis=1))
                h = np.logical_or(a2 <= 0, a4 <= 0)
                delta24 = np.sum(np.mean(np.sqrt(l13) * pacos((d13-a2-a4) / np.sqrt(a2 * a4 + h) / 2 * (1-h) + h),axis=1))
                h = np.logical_or(a1 <= 0, a2 <= 0)
                delta34 = np.sum(np.mean(np.sqrt(l12) * pacos((d12-a3-a4) / np.sqrt(a3 * a4 + h) / 2 * (1-h) + h),axis=1))

                r3=np.mean(np.sqrt(np.maximum((4 * a1 * a2 - (a1 + a2 - d12) **2) / (l34 + (l34<=0)) * (l34>0), 0)),axis=1) / 48

                lkc1[1,3] = (delta12+delta13+delta14+delta23+delta24+delta34)/(2 * np.pi)
                lkc1[2,4] = np.sum(np.mean(np.sqrt(a1) + np.sqrt(a2) + np.sqrt(a3) + np.sqrt(a4), 2))/8
                lkc1[3,3] = np.sum(r3)
                
                ## Original MATLAB code has a if nargout>=2 here, ignore it as no equivalent exists in Python - RV. 
                for j in range(0,4):
                    if f:
                        v1 = tet[masktet,j] + vs[k]
                    else:
                        v1 = tet[masktet,j] + vs[k+1]
                        v1 = v1 - int(v1 > vs[k+2]) * (vs[k+2] - vs[k])
                    reselspvert = reselspvert + accum(v1, r3, [v, 1])

            lkc = lkc + lkc1
            es = es + edg1.shape[0]

        ## Original MATLAB code has a if nargout>=2 here, ignore it as no equivalent exists in Python - RV. 
        D = 2 + (K>1)
        reselspvert = reselspvert.T / (D+1) / np.sqrt(4*np.log(2)) ** D

        
    ## Compute resels - RV
    D1 = lkc.shape[0]-1
    D2 = lkc.shape[1]-1
    tpltz = toeplitz((-1)**(np.arange(0,D1+1)), (-1)**(np.arange(0,D2+1)))
    lkcs = np.sum(tpltz * lkc, axis=1).T 
    lkcs = np.trim_zeros(lkcs,trim='b')
    lkcs = np.atleast_2d(lkcs)
    D = lkcs.shape[1]-1
    resels = lkcs / np.sqrt(4*np.log(2))**np.arange(0,D+1)

    return resels, reselspvert, edg