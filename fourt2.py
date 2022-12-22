import numpy as np
def fft(x,dt=0.2,t0=None):
    def fft_split(x0):
        print('fft on')
        print(x0)
        n_p = x0.size
        print('np =', n_p)
        even = x0[::2]
        odd = x0[1::2]
        if n_p==2:
            return even[0] - odd[0]
        else:
            even_x = fft_split(even)
            odd_x = fft_split(odd)
            jx = []
            for i in range(n_p//2):
                jx.append(even_x-odd_x*w_mat[i])
            return np.array(jx)

    n=x.size
    if t0 is None:
        t0 = dt*n
    else:
        dt = t0/n
    f0=1/dt
    w0=2*np.pi*f0
    n_l=np.arange(n)
    w_mat = np.exp(w0*n_l**2*1j)
    return fft_split(x)

if __name__ == '__main__':
    t = np.arange(0,1.6,0.2)
    print(t.shape)
    y = np.sin(2*np.pi*t)+np.sin(5*np.pi*t)
    jk = np.fft.fft(y)
    lmo = fft(y)
    print('\njk=')
    print(jk)
    print('\n found lmo=\n')
    print(lmo)