import numpy as np
import pandas as pd
import os

from scipy.special import erf
from tqdm import tqdm
from emcee import EnsembleSampler
from astropy import constants as const
from scipy import integrate, optimize, signal
from .func import *
from .classes import *
from scipy import special as sp
c = const.c.value

import pdb

#########################################################
#														#
#		PHOTOMETRIC + SPEC VERSION OF THE FITTING		#
#														#
#########################################################


def logpwIRS(theta, P):

	if len(theta) > 2:
		if (theta[0] < P[0][0]) | (theta[0] > P[0][1]) == True:
			return -np.inf
		if (theta[1] < P[1][0]) | (theta[1] > P[1][1]) == True:
			return -np.inf
		if (theta[2] < P[2][0]) | (theta[2] > P[2][1]) == True:
			return -np.inf
		if (theta[3] < P[3][0]) | (theta[3] > P[3][1]) == True:
			return -np.inf
		if (theta[4] < P[4][0]) | (theta[4] > P[4][1]) == True:
			return -np.inf
		if (theta[5] < 20.0) or (theta[5] > 75.):
			return -np.inf
		else:
			logp = np.log10(np.exp(-(np.log10(theta[5])-P[5][0])**2./2./P[5][1]/P[5][1]))
		if (theta[6] < P[6][0]) | (theta[6] > P[6][1]) == True:
			return -np.inf
		if (theta[7] < P[7][0]) | (theta[7] > P[7][1]) == True:
			return -np.inf
		return logp
	else:		
		if (theta[0] < P[0][0]) | (theta[0] > P[0][1]) == True:
			return -np.inf
		if (theta[1] < P[1][0]) | (theta[1] > P[1][1]) == True:
			return -np.inf
		return 0
	

def lnpostfnwIRS(theta, x, y, yerr, modelBG, modelSG, UL, wei, z, P):
	lp = logpwIRS(theta, P)
	if not np.isfinite(lp):
		return -np.inf
	return lp + loglwIRS(theta, x, y, yerr, modelBG, modelSG, UL, wei, z)

def loglwIRS(theta, x, y, yerr, modelBG, modelSG, UL, wei, z):

	if len(theta) > 2:
		lnDust, dlnPAH, lnAGN, alpha1, alpha2, coff, lsg, llg = theta
		
		modelAGN1 = 10**lsg * Gauss(x, np.log10(11.*(1.+z)), 0.05)
		modelAGN2 = 10**llg * Gauss(x, np.log10(19.*(1.+z)), 0.1)
		modelAGN3 = 10**lnAGN * AGNmodel(x, 15.*(1.+z), coff*(1.+z), alpha1, alpha2, -3.5)

		_modelAGN = modelAGN1 + modelAGN2 + modelAGN3

		if len(modelSG) > 0:
			lnPAH = (0.24 + 0.86 * lnDust) + dlnPAH
			_modelGal = 10**lnDust * modelBG + 10**lnPAH * modelSG
		else:
			_modelGal = 10**lnDust * modelBG
		
		model = _modelAGN + _modelGal

	else:
		lnDust, dlnPAH = theta

		if len(modelSG) > 0:
			lnPAH = (0.24 + 0.86 * lnDust) + dlnPAH
			model = 10**lnDust * modelBG + 10**lnPAH * modelSG
		else:
			model = 10**lnDust * modelBG

	#Upper limits loglikelihood
	logl_herschel = 0.
	o = np.where(UL == 1)[0]
	if len(o) > 0:
		logl_herschel += np.sum(0.5 + 0.5 * sp.erf((model[o]-y[o])/np.sqrt(2.)/(yerr[o]**2.)))
	
	dlambda = np.gradient(x)
	# Herschel loglikelihood aside from upper limits
	o = np.where((dlambda > 5.) & (UL == 0))[0]
	n_herschel = len(o)
	logl_herschel += -0.5*np.sum((model[o][1::] - y[o][1::])**2./(yerr[o][1::]**2.))

	o = np.where((dlambda < 5.) & (UL == 0))[0]
	n_irs = len(o)
	logl_irs = -0.5*np.sum((model[o] - y[o])**2./(yerr[o]**2.))

	logl = logl_irs * wei[0] + logl_herschel * wei[1]

	if logl != logl:
		raise ValueError('The loglikelihood is not a numerical value. Check your data.')

	return logl

def runSEDspecFit(lambdaObs, fluxObs, efluxObs,\
				  z = 0.01,\
				  filters = ['PACS70', 'PACS100', 'PACS160', 'SPIRE250ps', 'SPIRE350ps', 'SPIRE500ps'], \
				  wavToFit = [70., 100., 160., 250., 350., 500.],\
			  	  UL = [0., 0., 0., 0., 0., 0.], \
				  IRSobsCorr = True,\
				  Nmc = 500, nthreads = 1, pgrbar = 1, \
				  Pdust = [5., 15.], PdPAH = [-0.3, 0.3], Ppl = [-5., 5.], Pbreak = [1.5, 0.01], Pslope1 = [0., 5.], Pslope2 = [0., 5.], \
				  Plsg = [-5., 5.], Pllg = [-5., 5.],\
				  templ = ''):

	if len(templ) == 0:
		path = os.path.dirname(iragnsep.__file__)
		templ = pd.read_csv(path+'/B18_full.csv')

	# Extract the name of the templates
	keys = templ.keys().values
	nameTempl_gal = []
	nameTempl_PAH = []
	for key in keys:
		if str(key).startswith('gal'):
			if str(key).endswith('PAH') == False:
				nameTempl_gal.append(key)
			else:
				nameTempl_PAH.append(key)

	# Test that we have template for everything (if no galaxy then it crashes)
	if len(nameTempl_gal) == 0:
		raise ValueError('The galaxy template does not exist. The name of the column defining nuLnu for the galaxy template needs to start with "gal".')

	# define the wavelengths
	try:
		wavTempl = templ['lambda_mic']
	except:
		raise ValueError('Rename the wavelengths column of the template "lambda_mic".')

	# Throughout we assume the flux in Jansky and wavelength in micron
	dlambda = np.gradient(lambdaObs)
	IRSwav = np.concatenate([lambdaObs[dlambda<5.], [lambdaObs[dlambda>5.][0]]])
	IRSflux = np.concatenate([fluxObs[dlambda<5.], [fluxObs[dlambda>5.][0]]])
	eIRSflux = np.concatenate([efluxObs[dlambda<5.], [efluxObs[dlambda>5.][0]]])
	IRSwavRest = IRSwav/(1. + z)

	# We attempt to correct for obscuration if possible and if set by the User
	# for this we measure the tau9p7 (Sirocky2008 + Spoon2007 for the anchor wavelengths)
	if IRSobsCorr == True:
		try:
			IRSflux_corr, eIRSflux_corr, _tau9p7 = corrIRSobs(IRSwavRest, IRSflux, eIRSflux)
		except:
			IRSflux_corr = IRSflux
			eIRSflux_corr = eIRSflux
			_tau9p7 = -99.
			print('*******************')
			print('It has failed to correct the IRS spectrum for obscuration. The most likely explanation is redshift since it needs the restframe anchor ' + \
				   'wavelengths to measure the strength of the silicate absorption. The fit is continued without correcting for obscuration.')
			print('*******************')
			pass
	else:
		IRSflux_corr = IRSflux
		eIRSflux_corr = eIRSflux
		_tau9p7 = -99.

	# Put all together for the fit
	wavFit = np.concatenate([IRSwav, lambdaObs[dlambda>5.][1::]])
	fluxFit = np.concatenate([IRSflux_corr, fluxObs[dlambda>5.][1::]])
	efluxFit = np.concatenate([eIRSflux_corr, efluxObs[dlambda>5.][1::]])

	#Derive the weights that should be allocated to the IRS spectrum
	Npoints = float(len(fluxFit))
	Herwei = 1./((Npoints-len(IRSwav))/Npoints)
	IRSwei = 1./((len(IRSwav))/Npoints)

	# Prepare a vector for the Upper Lmits
	ULIRS = np.zeros(len(IRSwav))
	ULall = np.concatenate([ULIRS, UL])

	# Define the free parameters
	lsg_perTempl = []
	elsg_perTempl = []
	llg_perTempl = []
	ellg_perTempl = []
	lnAGN_perTempl = []
	elnAGN_perTempl = []
	coff_perTempl = []
	ecoff_perTempl = []
	alpha1_perTempl = []
	ealpha1_perTempl = []
	alpha2_perTempl = []
	ealpha2_perTempl = []
	
	lnDust_perTempl = []
	elnDust_perTempl = []
	lnPAH_perTempl = []
	elnPAH_perTempl = []
	
	logl_perTempl = []
	tplName_perTempl = []
	tau9p7_save = []
	AGNon = []
	nParms = []

	# We loop over the templates
	for name_i in nameTempl_gal:
		assert isinstance(name_i, str), "The list nameTempl requests strings as it corresponds to the names" + \
										" given to the various templates of galaxies to use for the fit."

		if pgrbar == 1:
			print("****************************************")
			print("  Fit of "+name_i+" as galaxy template  ")
			print("****************************************")

		# We prepare the templates by matching the IRS wavelengths
		# and the broad band fluxes now that we know the redshift.

		# Because the B18 contains Big Grains and PAHs, even if it's a single template
		# we put it in the big grains and test later to shut the PAH component
		nuLnuBGTempl = templ[name_i].values

		# Herschel Fluxes
		SEDgen = modelToSED(wavTempl, nuLnuBGTempl, z)
		fluxHerschel = []
		for filt in filters:
		 	fluxHerschel.append(getattr(SEDgen, filt)())

		# IRS fluxes
		Fnu = nuLnuToFnu(wavTempl, nuLnuBGTempl, z)
		IRSmodelFlux = np.interp(IRSwavRest, wavTempl, Fnu)
			
		modelBG = np.concatenate([IRSmodelFlux, fluxHerschel])

		if name_i.endswith('dust') == False:
			modelSG_wUnc = []
			emodelSG_wUnc = []
		else:
			nuLnuSGTempl = templ[nameTempl_PAH[0]].values

			# Herschel flux
			SEDgen = modelToSED(wavTempl, nuLnuSGTempl, z)
			fluxHerschel = []
			for filt in filters:
				fluxHerschel.append(getattr(SEDgen, filt)())

			#IRS spec
			Fnu = nuLnuToFnu(wavTempl, nuLnuSGTempl, z)
			IRSmodelFlux = np.interp(IRSwavRest, wavTempl, Fnu)
		
			modelSG = np.concatenate([IRSmodelFlux, fluxHerschel])

		# FIT WITHOUT THE AGN
		ndim = 2
		nwalkers = int(10. * ndim)

		parms = np.zeros(shape=(nwalkers, ndim))
		parms[:,0] = np.random.uniform(low = Pdust[0], high = Pdust[1], size=nwalkers) # norm Dust
		parms[:,1] = np.random.uniform(low = PdPAH[0], high = PdPAH[1], size=nwalkers) # norm PAH

		sampler = EnsembleSampler(nwalkers, ndim, lnpostfnwIRS, args=(wavFit, fluxFit, efluxFit, modelBG, modelSG, \
								  ULall, [IRSwei, Herwei], z, [Pdust, PdPAH]), threads = 1)

		if pgrbar == 1:
			with tqdm(total=Nmc) as pbar:
				for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
					pbar.update()
					pass
			print('------------------------')
		else:
			for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
				pass

		# Build the flat chain
		chain = sampler.chain.reshape([-1,ndim])

		# Save the results
		lnDust_perTempl.append(10**np.median(chain[:,0]))
		elnDust_perTempl.append(10**np.std(chain[:,0]))
		
		if name_i.endswith('dust') == False:
			lnPAH_perTempl.append(1e-20)
			elnPAH_perTempl.append(0.0)
		else:
			lnPAH_perTempl.append(10**(0.24 + 0.86 * np.median(chain[:,0]) + np.median(chain[:,1])))
			elnPAH_perTempl.append(10**(0.24 + 0.86 * np.std(chain[:,0] + np.std(chain[:,1]))))
		
		lnAGN_perTempl.append(-99.)
		elnAGN_perTempl.append(-99.)

		alpha1_perTempl.append(-99.)
		ealpha1_perTempl.append(-99.)

		alpha2_perTempl.append(-99.)
		ealpha2_perTempl.append(-99.)

		coff_perTempl.append(-99.)
		ecoff_perTempl.append(-99.)

		lsg_perTempl.append(-99.)
		elsg_perTempl.append(-99.)

		llg_perTempl.append(-99.)
		ellg_perTempl.append(-99.)

		logl_perTempl.append(loglwIRS([np.log10(lnDust_perTempl[-1]), np.median(chain[:,1])], \
		 					 wavFit, fluxFit, efluxFit,modelBG, modelSG, ULall, [IRSwei, Herwei], z))

		AGNon.append(0.)
		tau9p7_save.append(_tau9p7)

		tplName_perTempl.append(name_i)
		nParms.append(ndim)

		# INCLUDING THE AGN
		# MCMC fit
		ndim = 8
		nwalkers = int(10. * ndim)

		parms = np.zeros(shape=(nwalkers, ndim))
		parms[:,0] = np.random.uniform(low = Pdust[0], high = Pdust[1], size=nwalkers) # norm Dust
		parms[:,1] = np.random.uniform(low = PdPAH[0], high = PdPAH[1], size=nwalkers) # norm PAH
		parms[:,2] = np.random.uniform(low = Ppl[0], high = Ppl[1], size=nwalkers) # AGN PL Norm
		parms[:,3] = np.random.uniform(low = Pslope1[0], high = Pslope1[1], size=nwalkers) # alpha1
		parms[:,4] = np.random.uniform(low = Pslope2[0], high = Pslope2[1], size=nwalkers) # alpha2
		parms[:,5] = np.random.uniform(low = 21., high = 90., size=nwalkers) # Break
		parms[:,6] = np.random.uniform(low = Plsg[0], high = Plsg[1], size=nwalkers) # 10micron
		parms[:,7] = np.random.uniform(low = Pllg[0], high = Pllg[1], size=nwalkers) # 18micron

		sampler = EnsembleSampler(nwalkers, ndim, lnpostfnwIRS, args=(wavFit, fluxFit, efluxFit, modelBG, modelSG, \
								  ULall, [IRSwei, Herwei], z, [Pdust, PdPAH, Ppl, Pslope1, Pslope2, Pbreak, Plsg, Pllg]), threads = nthreads)

		if pgrbar == 1:
			with tqdm(total=Nmc) as pbar:
				for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
					pbar.update()
					pass
			print('------------------------')
		else:
			for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
				pass

		# Build the flat chain
		chain = sampler.chain.reshape([-1,ndim])
				
		# Save the results
		lnDust_perTempl.append(10**np.median(chain[:,0]))
		elnDust_perTempl.append(10**np.std(chain[:,0]))

		if name_i.endswith('dust') == False:
			lnPAH_perTempl.append(1e-20)
			elnPAH_perTempl.append(0.0)
		else:
			lnPAH_perTempl.append(10**(0.24 + 0.86 * np.median(chain[:,0]) + np.median(chain[:,1])))
			elnPAH_perTempl.append(10**(0.24 + 0.86 * np.std(chain[:,0] + np.std(chain[:,1]))))

		lnAGN_perTempl.append(10**np.median(chain[:,2]))
		elnAGN_perTempl.append(10**np.std(chain[:,2]))

		alpha1_perTempl.append(np.median(chain[:,3]))
		ealpha1_perTempl.append(np.std(chain[:,3]))

		alpha2_perTempl.append(np.median(chain[:,4]))
		ealpha2_perTempl.append(np.std(chain[:,4]))

		coff_perTempl.append(np.median(chain[:,5]))
		ecoff_perTempl.append(np.std(chain[:,5]))

		lsg_perTempl.append(10**np.median(chain[:,6]))
		elsg_perTempl.append(10**np.std(chain[:,6]))

		llg_perTempl.append(10**np.median(chain[:,7]))
		ellg_perTempl.append(10**np.std(chain[:,7]))


		theta = [np.log10(lnDust_perTempl[-1]), np.median(chain[:,1]), np.log10(lnAGN_perTempl[-1]), alpha1_perTempl[-1], \
						  alpha2_perTempl[-1], coff_perTempl[-1], np.log10(lsg_perTempl[-1]), np.log10(llg_perTempl[-1])]
		logl_perTempl.append(loglwIRS(theta, wavFit, fluxFit, efluxFit, modelBG, modelSG, ULall, [IRSwei, Herwei], z))

		AGNon.append(1.)
		tau9p7_save.append(_tau9p7)

		tplName_perTempl.append(name_i)
		nParms.append(ndim)

	# Find the best model and the Akaike weight
	bestModelInd, Awi = exctractBestModel(logl_perTempl, nParms, len(wavFit), corrected = False)
	bestModelFlag = np.zeros(len(AGNon))
	bestModelFlag[bestModelInd] = 1

	# QF = np.zeros(len(lnDust_perTempl))-99.

	# Save the results in a table
	resDict = {'normGal_dust': lnDust_perTempl, 'enormGal_dust': elnDust_perTempl, 'normGal_PAH': lnPAH_perTempl, 'enormGal_PAH': elnPAH_perTempl, \
			   'normAGN_PL': lnAGN_perTempl, 'enormAGN_PL': elnAGN_perTempl, 'lBreak_PL': coff_perTempl, 'elBreak_PL': ecoff_perTempl, \
			   'alpha1_PL': alpha1_perTempl, 'ealpha1_PL': ealpha1_perTempl,'alpha2_PL': alpha2_perTempl, 'ealpha2_PL': ealpha2_perTempl,\
			   'normAGN_G10': lsg_perTempl, 'enormAGN_G10': elsg_perTempl, 'normAGN_G18': llg_perTempl, 'enormAGN_G18': ellg_perTempl,\
			   'logl': logl_perTempl, 'AGNon': AGNon, 'tplName': tplName_perTempl, 'bestModelFlag': bestModelFlag, 'Aw': Awi, \
			   'tau9p7': tau9p7_save}

	dfRes = pd.DataFrame(resDict)

	return dfRes


#################################################
#												#
#		PHOTOMETRIC VERSION OF THE FITTING		#
#												#
#################################################
from scipy.stats import norm

def logp_photo(theta, modelAGN, P):
	if len(modelAGN) > 0:
		if (theta[0] < P[0][0]) | (theta[0] > P[0][1]) == True:
				return -np.inf
		if (theta[1] < P[1][0]) | (theta[1] > P[1][1]) == True:
		 		return -np.inf
		if (theta[2] < P[2][0]) | (theta[2] > P[2][1]) == True:
		 		return -np.inf
		if (theta[3] < P[3][0]) | (theta[3] > P[3][1]) == True:
		 		return -np.inf
	else:
		if (theta[0] < P[0][0]) | (theta[0] > P[0][1]) == True:
				return -np.inf
		if (theta[1] < P[1][0]) | (theta[1] > P[1][1]) == True:
		 		return -np.inf
	return 0.

def lnpostfn_photo(theta, x, y, yerr, modelBG, modelSG, modelAGN, modelSi, UL, P):
	lp = logp_photo(theta, modelAGN, P)
	if not np.isfinite(lp):
		return -np.inf
	
	return lp + logl_photo(theta, x, y, yerr, modelBG, modelSG, modelAGN, modelSi, UL)

def logl_photo(theta, x, y, yerr, modelBG, modelSG, modelAGN, modelSi, UL):

	# Unfold the parameters
	if len(modelAGN) > 1:
		lnDust, dlnPAH, lnAGN, lnSi = theta
	else:
		lnDust, dlnPAH = theta

	# Define the galaxy model (dust + PAH)
	if len(modelSG) > 0:
			lnPAH = (0.24 + 0.86 * lnDust) + dlnPAH
			_modelGal = 10**lnDust * modelBG + 10**lnPAH * modelSG
	else:
		_modelGal = 10**lnDust * modelBG

	# Define the model of the AGN
	if len(modelAGN) > 1:
		if len(modelSi) > 1:
			_modelAGN = 10**lnAGN * modelAGN + 10**lnSi * modelSi
		else:
			_modelAGN = 10**lnAGN * modelAGN
		ymodel = _modelGal + _modelAGN
	else:
		ymodel = _modelGal

	# Measure the log-likelihood, including upper limits
	logl = 0.
	o = np.where(UL == 1)[0]
	if len(o) > 0:
		logl += np.sum(0.5 + 0.5 * sp.erf((ymodel[o]-y[o])/np.sqrt(2.)/(yerr[o]**2.)))

	o = np.where(UL != 1)[0]
	logl += -0.5*np.sum((ymodel[o] - y[o])**2./(yerr[o]**2.))

	if logl == 0.:
		pdb.set_trace()

	return logl

def runSEDphotFit(lambdaObs, fluxObs, efluxObs, \
				  z = 0.01, \
				  filters = ['MIPS24', 'PACS70', 'PACS100', 'PACS160', 'SPIRE250', 'SPIRE350', 'SPIRE500'], \
				  wavToFit = [24., 70., 100., 160., 250., 350., 500.], \
				  UL = [0., 0., 0., 0., 0., 0., 0.], \
				  Nmc = 500, nthreads = 1, pgrbar = 1, \
				  NoSiem = False, \
				  Pdust = [5., 15.], PdPAH = [-0.3, 0.3], PnormAGN = [5., 15.], PSiEm = [5., 15.],\
				  templ = ''):


	if len(templ) == 0:
		path = os.path.dirname(iragnsep.__file__)
		templ = pd.read_csv(path+'/B18_full.csv')

	# Extract the name of the templates
	keys = templ.keys().values
	nameTempl_gal = []
	nameTempl_PAH = []
	nameTempl_AGN = []
	nameTempl_Siem = []
	for key in keys:
		if str(key).startswith('gal'):
			if str(key).endswith('PAH') == False:
				nameTempl_gal.append(key)
			else:
				nameTempl_PAH.append(key)
		if str(key).startswith('AGN'):
			if str(key).endswith('Siem'):
				nameTempl_Siem.append(key)
			else:
				nameTempl_AGN.append(key)

	# Test that we have template for everything (if no galaxy then it crashes)
	if len(nameTempl_gal) == 0:
		raise ValueError('The galaxy template does not exist. The name of the column defining nuLnu for the galaxy template needs to start with "gal".')

	# define the wavelengths
	try:
		wavTempl = templ['lambda_mic']
	except:
		raise ValueError('Rename the wavelengths column of the template "lambda_mic".')

	# Throughout we assume the flux in Jansky and wavelength in micron
	# Put all together for the fit
	wavFit = lambdaObs
	fluxFit = fluxObs
	efluxFit = efluxObs

	# wavelength for the templates
	try:
		wavTempl = templ.lambda_mic.values
	except:
		raise Exception('Rename the wavelength column in the template file to "lambda_mic".')

	# Define the free parameters
	lnAGN_perTempl = []
	elnAGN_perTempl= []

	lnSi_perTempl = []
	elnSi_perTempl = []

	lnDust_perTempl = []
	elnDust_perTempl = []

	lnPAH_perTempl = []
	elnPAH_perTempl = []

	logl_perTempl = []
	tplNameGal_perTempl = []
	tplNameAGN_perTempl = []
	AGNon = []
	nParms = []

	# We loop over the templates
	for name_i in nameTempl_gal:
		assert isinstance(name_i, str), "The list nameTempl requests strings as it corresponds to the names" + \
										" given to the various templates of galaxies to use for the fit."

		if pgrbar == 1:
			print("****************************************")
			print("  Fit of "+name_i+" as galaxy template  ")
			print("****************************************")

		# Because the B18 contains Big Grains and Small grains, even if it's a single template
		# we put it in the BG grains and test later to shut the small grain component
		
		nuLnuBGTempl = templ[name_i].values
		# Convert to photometric flux
		SEDgen = modelToSED(wavTempl, nuLnuBGTempl, z)
		modelBG = []
		for filt in filters:
			modelBG.append(getattr(SEDgen, filt)())

		modelBG = np.array(modelBG)

		if name_i.endswith('dust') == False:
			modelSG = []
			emodelSG = []
		else:	
			nuLnuSGTempl = templ['gal_PAH'].values
			SEDgen = modelToSED(wavTempl, nuLnuSGTempl, z)
			modelSG = []
			for filt in filters:
				modelSG.append(getattr(SEDgen, filt)())

			modelSG = np.array(modelSG)

		# FIT WITHOUT THE AGN
		ndim = 2
		nwalkers = int(10. * ndim)

		parms = np.zeros(shape=(nwalkers, ndim))
		parms[:,0] = np.random.uniform(low = Pdust[0], high = Pdust[1], size=nwalkers) # norm Dust
		parms[:,1] = np.random.uniform(low = PdPAH[0], high = PdPAH[1], size=nwalkers) # norm PAH

		sampler = EnsembleSampler(nwalkers, ndim, lnpostfn_photo, args=(wavFit, fluxFit, efluxFit, modelBG, modelSG, [], [], \
								  UL,[Pdust, PdPAH]), threads = 1)

		if pgrbar == 1:
			with tqdm(total=Nmc) as pbar:
				for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
					pbar.update()
					pass
			print('------------------------')
		else:
			for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
				pass

		# Build the flat chain
		chain = sampler.chain.reshape([-1,ndim])

		lnSi_perTempl.append(-99.)
		elnSi_perTempl.append(-99.)

		lnAGN_perTempl.append(-99.)
		elnAGN_perTempl.append(-99.)

		lnDust_perTempl.append(10**np.median(chain[:,0]))
		elnDust_perTempl.append(10**np.std(chain[:,0]))

		if name_i.endswith('dust') == False:
			lnPAH_perTempl.append(1e-20)
			elnPAH_perTempl.append(0.0)
		else:
			lnPAH_perTempl.append(10**(0.24 + 0.86 * np.median(chain[:,0]) + np.median(chain[:,1])))
			elnPAH_perTempl.append(10**(0.24 + 0.86 * np.std(chain[:,0] + np.std(chain[:,1]))))

		logl_perTempl.append(logl_photo([np.log10(lnDust_perTempl[-1]), np.median(chain[:,1])], wavFit, fluxFit, efluxFit,modelBG, modelSG, [], [], UL))

		AGNon.append(0.)
		nParms.append(ndim)
		tplNameGal_perTempl.append(name_i)
		tplNameAGN_perTempl.append(str('N/A'))

		# INCLUDE THE AGN
		for AGN_i in nameTempl_AGN:

			nuLnu_AGN = templ[AGN_i].values
			SEDgen = modelToSED(wavTempl, nuLnu_AGN, z)
			modelAGN = []
			for filt in filters:
				modelAGN.append(getattr(SEDgen, filt)())

			modelAGN = np.array(modelAGN)

			modelSiem = []
			if NoSiem == False:
				nuLnu_Siem = templ[nameTempl_Siem].values.flatten()
				SEDgen = modelToSED(wavTempl, nuLnu_Siem, z)
				for filt in filters:
					modelSiem.append(getattr(SEDgen, filt)())

				modelSiem = np.array(modelSiem)
			
			ndim = 4
			nwalkers = int(10. * ndim)

			parms = np.zeros(shape=(nwalkers, ndim))
			parms[:,0] = np.random.uniform(low = Pdust[0], high = Pdust[1], size=nwalkers) # Norm Galaxy
			parms[:,1] = np.random.uniform(low = PdPAH[0], high = PdPAH[1], size=nwalkers)
			parms[:,2] = np.random.uniform(low = PnormAGN[0], high = PnormAGN[1], size=nwalkers) # NormAGN
			parms[:,3] = np.random.uniform(low = PSiEm[0], high = PSiEm[1], size=nwalkers) # NormSi

			sampler = EnsembleSampler(nwalkers, ndim, lnpostfn_photo, args=(wavFit, fluxFit, efluxFit, modelBG, modelSG, modelAGN, modelSiem, np.array(UL), \
									  [Pdust, PdPAH, PnormAGN, PSiEm]), threads = nthreads)

			#Perform the Fit Using MCMC
			if pgrbar == 1:
				with tqdm(total=Nmc) as pbar:
					for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
						pbar.update()
						pass
				print('------------------------')
			else:
				for p, lnprob, rstate in sampler.sample(parms, iterations = Nmc):
					pass

			#pdb.set_trace()
			# Build the flat chain
			chain = sampler.chain.reshape([-1,ndim])

			lnDust_perTempl.append(10**np.median(chain[:,0]))
			elnDust_perTempl.append(10**np.std(chain[:,0]))

			if name_i.endswith('dust') == False:
				lnPAH_perTempl.append(1e-20)
				elnPAH_perTempl.append(0.0)
			else:
				lnPAH_perTempl.append(10**(0.24 + 0.86 * np.median(chain[:,0]) + np.median(chain[:,1])))
				elnPAH_perTempl.append(10**(0.24 + 0.86 * np.std(chain[:,0] + np.std(chain[:,1]))))

			lnAGN_perTempl.append(10**np.median(chain[:,2]))
			elnAGN_perTempl.append(10**np.std(chain[:,2]))

			if (NoSiem == True):
				lnSi_perTempl.append(1e-20)
				elnSi_perTempl.append(0.0)
			else:
				lnSi_perTempl.append(10**np.median(chain[:,3]))
				elnSi_perTempl.append(10**np.std(chain[:,3]))

			AGNon.append(1.)
			nParms.append(ndim)
			tplNameGal_perTempl.append(name_i)
			tplNameAGN_perTempl.append(AGN_i)

			logl_perTempl.append(logl_photo([np.log10(lnDust_perTempl[-1]), np.median(chain[:,1]), np.log10(lnAGN_perTempl[-1]), np.log10(lnSi_perTempl[-1])], \
								 wavFit, fluxFit, efluxFit,modelBG, modelSG, modelAGN, modelSiem, UL))

	# Find the best model and the Akaike weight
	bestModelInd, Awi = exctractBestModel(logl_perTempl, nParms, len(wavFit), corrected = True)
	bestModelFlag = np.zeros(len(AGNon))
	bestModelFlag[bestModelInd] = 1

	# Save the results in a table
	resDict = {'normGal_dust': lnDust_perTempl, 'enormGal_dust': elnDust_perTempl, 'normGal_PAH': lnPAH_perTempl, 'enormGal_PAH': elnPAH_perTempl, \
			   'normAGN': lnAGN_perTempl, 'enormAGN': elnAGN_perTempl, 'normSiem': lnSi_perTempl, 'enormSi': elnSi_perTempl, \
			   'logl': logl_perTempl, 'AGNon': AGNon, 'tplName_gal': tplNameGal_perTempl, 'tplName_AGN': tplNameAGN_perTempl,'bestModelFlag': bestModelFlag, 'Aw': Awi}

	dfRes = pd.DataFrame(resDict)

	return dfRes