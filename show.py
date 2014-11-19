from IPython.display import Image as show_img
from IPython.display import display
from io import BytesIO
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# utility for displaying things in Ipython

def show(I, bound=False):
    bio = BytesIO()
    if type(I) is np.ndarray:
        I = I.astype('float')
        if I.shape[0]<50:
            I = grow(I)
        mx = np.max(I)
        mn = np.min(I)
        print mx, mn
        if bound:
            I = 255*(I-mn)/(mx-mn)
        im = Image.fromarray(I.astype('uint8'))
	im.save(bio, format='png')
    elif isinstance(I, Image.Image): 
	I.save(bio, format='png')
    elif isinstance(I, plt.Figure):
        buf = BytesIO()
        I.savefig(bio, format = 'png')
        #buf.seek(0)
        #im = Image.open(buf)
    else:
        return

    display(show_img(bio.getvalue(), format='png'))

def grow(I, m=10):
    w,h = I.shape
    II = np.empty((w*m,h*m), dtype=I.dtype)
    for i in range(w):
        for j in range(h):
            II[i*m:(i+1)*m,j*m:(j+1)*m]=I[i,j]
    return II
