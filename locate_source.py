import numpy
from scipy import optimize


def amplitude_attenuation(dists): 
	""" 
	basic model for sound amplitude falloff over distance
	other possibly better models might include high-frequency/low-freq ratio falloff
	due to diffraction and absorption

	signal strength in this case is assumed to be sound pressure which has an inverse relationship to distance
	"""
	return 1./dists


def locate_source(arr, guess=None, fun=amplitude_attenuation):
	"""
	arr   ... 3xN array of sensor locations and measured signal strength
	      ... x0, y0, a0
	      ... x1, y1, a1
	guess ... x,y pair of prev known position or best guess at current location

	fun ... function that relates distance to signal strength: fun(dist)=sig_strength
	
	"""

	if guess is None:
		# set init guess to the sensor location with strongest signal
		#guess = arr[numpy.argmax(arr[:,2]), 0:2]
		# set init guess to sensor strength weighted average
		ws = arr[:,1]
		gx = (arr[:,0]*ws).sum()/ws.sum()
		gy = (arr[:,1]*ws).sum()/ws.sum()
		guess = [gx,gy]

	def f(x):
		#print 'iter', x
		vals1 = arr[:,2]
		vals2 = fun(get_dists(arr, x) )
		return numpy.sum((vals1 - vals2)**2)

	#print 'init guess', guess
	r = optimize.minimize(f, guess, method='Nelder-Mead')
	#print 'final soln', r.x
	return r.x

def get_dists(arr, center):
	return numpy.sqrt(numpy.sum( (arr[:,:2] - center)**2, 1) )


rnd =  numpy.random.random


class Test:

	def __init__(self, fun=amplitude_attenuation, noise=.1, n_sensors=4):
		self.arr = numpy.empty((n_sensors,3))
		self.source_pos = numpy.zeros((2,), dtype=float)
		self.fun = fun
		self.noise = noise
		self.n_sensors = n_sensors
		self.reset()

	def reset(self):
		"""
		generate a random array of sensors
		randomly select a target location
		comupte theoretical signal for each sensor
		optionally add noise (random variation in signal strength)
		"""
		n_sensors = self.n_sensors
		self.arr[:,0] = rnd(n_sensors)
		self.arr[:,1] = rnd(n_sensors)
		self.source_pos[:] = rnd(2)
		self.set_sensors()

	def set_sensors(self):	
		dists = get_dists(self.arr, self.source_pos)
		self.arr[:,2] = self.fun(dists) + (rnd(self.n_sensors)-.5)*self.noise

	def bbox(self, pad=.1, aspect=1.):
		arr = self.arr
		pt = self.source_pos
		xmin = min(arr[:,0].min(), pt[0])
		xmax = max(arr[:,0].max(), pt[0])
		ymin = min(arr[:,1].min(), pt[1])
		ymax = max(arr[:,1].max(), pt[1])
		xrng = (xmax-xmin)*(1+pad)
		yrng = (ymax-ymin)*(1+pad)
		xmid = (xmax+xmin)/2.
		ymid = (ymax+ymin)/2.
		if xrng>yrng*aspect: 
			yrng = xrng/aspect
		else:
			xrng = yrng*aspect
		return [[xmid-xrng/2., ymid-yrng/2.], [xmid+xrng/2., ymid+yrng/2.]]


	def heatmap(self, shape=(100,100), pad=.1):
		xct, yct = shape
		bbox = self.bbox(aspect=float(xct)/yct, pad=pad)
		bbox = [0.,0.],[1.,1.]
		[x0,y0],[x1,y1] = bbox
		xs = numpy.linspace(x0,x1,xct)
		yx = numpy.linspace(y0,y1,yct)
		x,y = numpy.meshgrid(xs,yx)
		d = numpy.sqrt((x-self.source_pos[0])**2 + (y-self.source_pos[1])**2)
		z1 = self.fun(d)
		z2 = numpy.zeros_like(z1)
		for px,py,v1 in self.arr:
			v2 = self.fun(numpy.sqrt((x-px)**2+(y-py)**2))
			z2 += (v1-v2)**2

		z2 = numpy.sqrt(z2)

		return x,y,z1,z2



