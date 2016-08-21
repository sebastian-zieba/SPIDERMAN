import matplotlib as mpl
#mpl.use('Agg')
import spiderman as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib._png import read_png
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, \
    AnnotationBbox
import matplotlib.patches as patches
from matplotlib import gridspec
import seaborn as sb
from numpy.random import randn
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os.path
import batman

def get_star_png():
	spiderdir = os.path.dirname(sp.__file__)
	png_name = os.path.join(spiderdir,'art/sun_transp.png')
	image = read_png(png_name)
	return image

def plot_system(spider_params,t,ax=False,min_temp=False,max_temp=False,temp_map=False,min_bright=0):
	if ax == False:
		f, ax = plt.subplots()
	image = sp.get_star_png()

	star_r_pix = 180
	star_offset_pix = 200

	p_imrat = star_r_pix*spider_params.rp

	coords = sp.separation_of_centers(t,spider_params)

	planet_pix = [star_offset_pix - coords[0]*p_imrat,star_offset_pix - coords[1]*p_imrat]

	ax = sp.plot_planet(spider_params,t,ax=ax,min_temp=min_temp,max_temp=max_temp,temp_map=temp_map,min_bright=min_bright,scale_planet=p_imrat,planet_cen=planet_pix)

	if(abs(abs(spider_params.phase)-0.5) > 0.25):
		#in front 
		s_zorder = 1
	else:
		s_zorder = 3

	im = ax.imshow(image,zorder=s_zorder)
	patch = patches.Circle((200, 200), radius=200, transform=ax.transData)
	im.set_clip_path(patch)

	ax.set_xlim(star_offset_pix+40*p_imrat,star_offset_pix+-40*p_imrat)
	ax.set_ylim(star_offset_pix+-10*p_imrat,star_offset_pix+10*p_imrat)



def plot_planet(spider_params,t,ax=False,min_temp=False,max_temp=False,temp_map=False,min_bright=0,scale_planet=1.0,planet_cen=[0.0,0.0]):

	if ax == False:
		f, ax = plt.subplots()
		new_ax = True
	else:
		new_ax = False

	planet = sp.generate_planet(spider_params,t)

	if temp_map == True:
		b_i = 17
	else:
		b_i = 16


	thetas = np.linspace(planet[0][10],planet[0][11],100)
	r = planet[0][14]*scale_planet
	radii = [0,r]

	xs = np.outer(radii, np.cos(thetas))+ planet_cen[0]
	ys = np.outer(radii, np.sin(thetas))+ planet_cen[1]
	xs[1,:] = xs[1,::-1]
	ys[1,:] = ys[1,::-1]

	if min_temp == False:
		temps = planet[:,b_i]
		min_temp = np.min(temps)
		max_temp = np.max(temps)


	dp = (min_temp*min_bright)

	val = (dp + planet[0][b_i]-min_temp)/(dp + max_temp-min_temp)

	c = plt.cm.inferno(val)
	ax.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)

	for j in range (1,len(planet)):
		val = (dp + planet[j][b_i]-min_temp)/(dp + max_temp-min_temp)
		c = plt.cm.inferno(val)

		n = planet[j]

		r1 = n[13]*scale_planet
		r2 = n[14]*scale_planet
		radii = [r1,r2]

		thetas = np.linspace(n[10],n[11],100)

		xs = np.outer(radii, np.cos(thetas)) + planet_cen[0]
		ys = np.outer(radii, np.sin(thetas)) + planet_cen[1]

		xs[1,:] = xs[1,::-1]
		ys[1,:] = ys[1,::-1]

		ax.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)
		ax.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)

	ax.set_axis_bgcolor('black')

	ax.spines['bottom'].set_color("black")
	ax.spines['left'].set_color("black")

	if new_ax == True:
		bs = 1.1
		ax.set_xlim(+bs,-bs)
		ax.set_ylim(-bs,+bs)

	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	divider = make_axes_locatable(ax)
	# Append axes to the right of ax, with 20% width of ax

	zero_temp = min_temp - dp
	data = [np.linspace(zero_temp,max_temp,1000)]*2
	fake, fake_ax = plt.subplots()
	mycax = fake_ax.imshow(data, interpolation='none', cmap=plt.cm.inferno)
	plt.close(fake)

	cax = divider.append_axes("right", size="20%", pad=0.05)
#	cbar = plt.colorbar(mycax, cax=cax,ticks=[1100,1300,1500,1700,1900])
	cbar = plt.colorbar(mycax, cax=cax)
	cbar.ax.tick_params(colors=("#04d9ff"))

	if temp_map == True:
		cbar.set_label('T (K)',color=("#04d9ff"))  # horizontal colorbar
	else:
		cbar.set_label('Relative brightness',color=("#04d9ff"))  # horizontal colorbar

	return ax

def make_movie():
	#sb.set_style("ticks")

	exp_time = 103.129

	tc = 200.0
	per = 0.81347753
	a = 0.01526
	inc = 82.33
	ecc = 0.0
	omega = 90
	a_rs = 4.855
	rp = 0.15938366414961666

	T_n = 1384.463713618203
	delta_T = 495.64620450883035
	xi = 0.30020002792596134

	T_n = 1127.8096575845159
	delta_T = 941.89297550917024
	xi = 0.64556829219408363

	u1 = 0
	u2 = 0

	T_s = 4520

	n_slice = 5

	n_ts = 100

	ts = np.linspace(tc-per,tc,n_ts)

	ps = ((ts-tc)/per)

	data = np.loadtxt('WASP43_HST13467/lc_cor_out.txt')

	ps_corr = data[:,0]
	lc_corr = data[:,1]

	for i in range(0,len(ps)):
		if(ps[i] > 1):
			ps[i] = ps[i] - np.floor(ps[i])
		if(ps[i] <= 0):
			ps[i] = ps[i] - np.ceil(ps[i]) + 1
		if(ps[i] == 1):
			ps[0] = 0

	pc = web.lightcurve(n_slice,ts,tc,per,a,inc,ecc,omega,a_rs,rp,xi,T_n,delta_T,u1,u2,T_s)

	bat_params = batman.TransitParams()
	bat_params.t0 = tc
	bat_params.t_secondary = tc+per/2.0
	bat_params.per = per
	bat_params.rp = rp
	bat_params.a = a_rs
	bat_params.inc = inc
	bat_params.ecc = ecc
	bat_params.w = omega
	bat_params.u = [0.4, 0]
	bat_params.limb_dark = "quadratic"		#FIXME - specify this value in one of the config files

	m = batman.TransitModel(bat_params, ts, supersample_factor=3, exp_time = exp_time/24./60./60.)

	lc = pc + (m.light_curve(bat_params)-1.0)

	phase_c = []
	phases = []

	ratio = 1/rp
	star_r = ratio

	dp = (T_n*0.1)
	min_temp = T_n
	max_temp = (T_n + delta_T)


	star_r_pix = 180
	star_offset_pix = 200

	p_imrat = star_r_pix*rp

	fn = 'sun_transp.png'
	image = read_png(fn)

	zero_temp = min_temp - dp

	data = [np.linspace(zero_temp,max_temp,1000)]*2

	cax = plt.imshow(data, interpolation='none', cmap=plt.cm.inferno)
	plt.close()

	for i in range(0,n_ts-1):
		t = ts[i]
		coords = web.separation_of_centers(t,tc,per,a,inc,ecc,omega,a_rs,ratio)

		star_x = 0.0-coords[0]
		star_y = 0.0-coords[1]
		star_z = 0.0-coords[2]

		ni = str(i)

		if len(ni) < 2:
			ni = '0'+ni

		plotname = 'plots/blooper_'+'{:03d}'.format(i)+'.png'

		phase = ((t-tc)/per)

		if(phase > 1):
			phase = phase - np.floor(phase)
		if(phase < 0):
			phase = phase + np.ceil(phase) + 1

		lambda0 = (np.pi + phase*2*np.pi)
		phi0 = np.arctan2(star_y,star_z)
		if(lambda0 > 2*np.pi):
			lambda0 = lambda0 - 2*np.pi;
		if(lambda0 < -2*np.pi):
			lambda0 = lambda0 + 2*np.pi;


		phases += [phase]

		planet = np.array(web.generate_planet(n_slice,xi,T_n,delta_T,lambda0,phi0,u1,u2))

		ax1 = plt.subplot(211, aspect='equal')

		gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1]) 

		with sb.axes_style("ticks"):
			ax2 = plt.subplot(gs[2])
			sb.despine()

		ax3 = plt.subplot(gs[3], aspect='equal')

		phase_c += [np.sum(planet[:,16])]

		thetas = np.linspace(planet[0][10],planet[0][11],100)
		r = planet[0][14]
		radii = [0,r]
		xs = star_offset_pix+ p_imrat*np.outer(radii, np.cos(thetas)) + coords[0]*p_imrat
		ys = star_offset_pix+ p_imrat*np.outer(radii, np.sin(thetas)) + coords[1]*p_imrat
		xs[1,:] = xs[1,::-1]
		ys[1,:] = ys[1,::-1]

		val = (dp + planet[0][17]-min_temp)/(dp + max_temp-min_temp)

		c = plt.cm.inferno(val)
		ax1.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)
		ax3.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)

		for j in range (1,len(planet)):

			val = (dp + planet[j][17]-min_temp)/(dp + max_temp-min_temp)
			c = plt.cm.inferno(val)

			n = planet[j]

			r1 = n[13]
			r2 = n[14]
			radii = [r1,r2]

			thetas = np.linspace(n[10],n[11],100)

			xs = star_offset_pix+ p_imrat*np.outer(radii, np.cos(thetas)) - coords[0]*p_imrat
			ys = star_offset_pix+ p_imrat*np.outer(radii, np.sin(thetas)) - coords[1]*p_imrat

			xs[1,:] = xs[1,::-1]
			ys[1,:] = ys[1,::-1]

			ax1.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)
			ax3.fill(np.ravel(xs), np.ravel(ys), edgecolor=c,color=c,zorder=2)


		thetas = np.linspace(planet[0][10],planet[0][11],100)
		radii = [0,star_r]
		xs = np.outer(radii, np.cos(thetas))
		ys = np.outer(radii, np.sin(thetas))
		xs[1,:] = xs[1,::-1]
		ys[1,:] = ys[1,::-1]
		c = plt.cm.inferno(1.0)

		if(abs(abs(phase)-0.5) > 0.25):
			#in front 
			s_zorder = 1
		else:
			s_zorder = 3

		ax1.set_axis_bgcolor('black')

		ax1.set_xlim(star_offset_pix+40*p_imrat,star_offset_pix+-40*p_imrat)
		ax1.set_ylim(star_offset_pix+-10*p_imrat,star_offset_pix+10*p_imrat)

		ax1.get_xaxis().set_visible(False)
		ax1.get_yaxis().set_visible(False)

		im = ax1.imshow(image,zorder=s_zorder)

		patch = patches.Circle((200, 200), radius=200, transform=ax1.transData)
		im.set_clip_path(patch)

		ax1.set_axis_bgcolor('black')
		ax2.set_axis_bgcolor('black')
		ax3.set_axis_bgcolor('black')

		ax1.spines['bottom'].set_color("black")
		ax1.spines['left'].set_color("black")
		ax3.spines['bottom'].set_color("black")
		ax3.spines['left'].set_color("black")

		ax2.spines['bottom'].set_color("#04d9ff")
		ax2.spines['left'].set_color("#04d9ff")

		ax2.xaxis.label.set_color("#04d9ff")
		ax2.yaxis.label.set_color("#04d9ff")

		ax2.plot(ps[:(i+1)],lc[:(i+1)],lw=2,color=("#04d9ff"))

		ax2.plot(ps_corr,lc_corr,',',color=("#04d9ff"))

	#	ax2.set_xlim(ps[0],ps[-1])
	#	ax2.set_ylim(np.median(lc)+1.1*(np.min(lc) - np.median(lc)),np.median(lc)+1.1*(np.max(lc) - np.median(lc)))

		ax2.set_xlim(0-0.02,1+0.02)

		ax2.set_ylabel('Relative flux')
		ax2.set_xlabel('Phase')

		ax2.set_ylim(0.9995,1.0009)
		ax2.set_yticks([0.9996,0.9998,1.0000,1.0002,1.0004,1.0006,1.0008])
		ax2.set_yticklabels(['0.9996','0.9998','1.0000','1.0002','1.0004','1.0006','1.0008'])


		bs = 1.1*p_imrat

		p_xpos = star_offset_pix - coords[0]*p_imrat
		p_ypos = star_offset_pix - coords[1]*p_imrat

		ax3.set_xlim(p_xpos+bs,p_xpos-bs)
		ax3.set_ylim(p_ypos-bs,p_ypos+bs)

		ax3.get_xaxis().set_visible(False)
		ax3.get_yaxis().set_visible(False)

		im = ax1.imshow(image,zorder=s_zorder)


		fig = plt.gcf()

		divider3 = make_axes_locatable(ax3)
		# Append axes to the right of ax3, with 20% width of ax3

		cax3 = divider3.append_axes("right", size="20%", pad=0.05)

		cbar3 = plt.colorbar(cax, cax=cax3,ticks=[1100,1300,1500,1700,1900])

		cbar3.ax.tick_params(colors=("#04d9ff"))

		cbar3.set_label('T (K)',color=("#04d9ff"))  # horizontal colorbar

		ax2.tick_params(axis='x', colors=("#04d9ff"))
		ax2.tick_params(axis='y', colors=("#04d9ff"))

		plt.tight_layout(pad=1.0)

		plt.savefig(plotname, bbox_inches='tight',pad_inches = 0.1,facecolor='black')

	#	plt.show()

		plt.close()