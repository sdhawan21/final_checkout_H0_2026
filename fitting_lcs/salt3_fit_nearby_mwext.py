## SALT3 fitter for the local calibrator sample 

## Procedure 1: fit everything with modelcov = True

## Procedure 2: fit all the data (optical) with no SNR cuts - modelcov = False
## Take the data within the [-10, 50] range, fit with modelcov = True


## Notes on how this organisation is going
## Step 1: only fitting the optical data for all SNe -> this might be the best 


## Also includes the plotting function for SNANA -> from the Pantheon+ fitted parameters

import numpy as np
import matplotlib.pyplot as plt
import os, sys, glob
import pandas as pd 
import sncosmo
import bp_registry 
import sfdmap 
import dustmaps
import astropy.units as u 

from astropy.table import Table
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
from SNmodel import io
#from plot_utils import * 
from time import time 
from sncosmo import SALT3Source
from dustmaps.planck import PlanckQuery
from dustmaps.leike2020 import Leike2020Query
from dustmaps.bayestar import BayestarQuery
from dustmaps.gaia_tge import GaiaTGEQuery
# a silly thing to keep track of here is a 
# pathway mismatch, since we need to import the propagation effects from
# the previous layer directory 
# the paths to the outputs and inputs are "../" and not "../../" 
# the latter will make things a bit complicated since then the outputs 
# are stored outside the main directory and you're going to take ages to find 
# the output - or some pathway errors will creep up
# Thanks.
os.chdir('../')
from  prop_effects_sncosmo import Fitzpatrick19
#os.chdir('fitting_tests/')

PlanckDust = PlanckQuery()
#LeikeDust = Leike2020Query()
#BayestarDust = BayestarQuery()
#GaiaDust = GaiaTGEQuery()


snmodel_str = sys.argv[3]
cov = bool(sys.argv[4])
fitter_val = sys.argv[5]
valid_model_arr = ['salt2', 'salt3', 'dove'] 
valid_fitter = ['minuit', 'mcmc']
assert snmodel_str in valid_model_arr
print(fitter_val)
assert fitter_val in valid_fitter
dustmod = sys.argv[6]
dustmod_vals = ['CCM89', 'F99', 'F19']

dustmap_val = sys.argv[7]
# how the dust map is used is in the for loop (unfortunately that was the best place to put it)
dustmap_val_arr = ['Leike2020', 'Planck', 'SF11', 'Bayestar', 'gaia']
assert dustmap_val in dustmap_val_arr
 


if dustmod == 'CCM89': 
    dustmod_str = sncosmo.CCM89Dust()
elif dustmod == 'F99': 
    dustmod_str = sncosmo.F99Dust()
elif dustmod == 'F19':
    dustmod_str = Fitzpatrick19()

if snmodel_str == 'salt2': 
    version_val = 'T21'
    snmodel = sncosmo.models.get_source(snmodel_str, version=version_val)

elif snmodel_str == 'salt3': 
    snmodel = sncosmo.models.get_source(snmodel_str)

elif snmodel_str == 'dove': 
    #snmodel = 
    #snmodel = SALT3Source(modeldir='../../../SALT3.DOVEKIE/')
    snmodel = SALT3Source(modeldir='../SALT3.DOVEKIE/')

filter_keys = {'E':'KAIT4-E', 'F':'KAIT4-F', 'G':'KAIT4-G', 'H':'KAIT4-H', 'M': 'nickel2-M'
, 'N':'nickel2-N', 'O':'nickel2-O', 'P':'nickel2-P', 'a':'KAIT1-a', 'b':'KAIT1-b', 'c':'KAIT1-c', 'd':'KAIT1-d',
'e':'KAIT2-e', 'f':'KAIT2-f', 'g':'KAIT2-g', 'h':'KAIT2-h'}

model = sncosmo.Model(snmodel, effects=[dustmod_str],
                           effect_names=['MW'],
                           effect_frames=['obs'])
lc_path = sys.argv[1]
lcs = glob.glob(lc_path+'/*')
#print(lcs)

# remove 10afx; why is it there
# remove the LIST file from Foundation
if 'Foundation' in lcs[0]: 
    lcs = [ii for ii in lcs if 'LIST' not in ii and 'README' not in ii and 'IGNORE' not in ii]
#sys.exit()
dustmaps = sfdmap.SFDMap(os.environ['SFD_DIR'])
# remove ps1-10afx and any directory with old in the name
lcs = [val for val in lcs if 'ps1' not in val and 'old' not in val and 'checked' not in val and 'snpy_converted_missing' not in val]

csp_ab_offset = {'CSP-g':-0.017, 'CSP-r':-0.006, 'CSP-i':+0.001, 'CSP-u':-0.058,
                  'g-CSP':-0.017, 'r-CSP':-0.006, 'i-CSP':+0.001, 'u-CSP':-0.058 }

csp_vegnat_offset = {'CSP-B':0.03, 'CSP-m':0.0096, 'CSP-o':0.0145, 'CSP-n':0.0096, 'CSP-V':0.0096, 'B-CSP':0.03, 'm-CSP':0.0096, 'o-CSP':0.0145, 'n-CSP':0.0096, 'V-CSP':0.0096}

cfa_ab_offset = {'cfa4-r':+0.004349,'cfa4-s':-0.003194, 'cfa4-n':+0.004349, 'cfa4-o':-0.003194, "rk1": +0.003501, "ik1": -0.003294}

cfa_vegnat_offset = {'cfa4-l':0.03,'cfa4-m':0.03, 'cfa4-p':0.03, 'cfa4-q':0.03, 'Bk1':0.03, 'Vk1':0.03}#, 'B4sh':, 'V4sh':, 'R4sh':, 'I4sh':}

vega_filt = ['Bs', 'Vs', 'Rs', 'Is', 'Us', 'B4sh', 'V4sh',  'Bk2', 'Vk2', 'cfa4-l', 'cfa4-m', 'cfa4-p',  'cfa4-q', 'NLB_B', 'NLB_V']
# I've written the CSP filters both ways around since the convention has changed depending on the 
# source of the files
ab_filt = ['u_CSP','g_CSP','r_CSP', 'i_CSP', 'CSP-u', 'CSP-r', 'CSP-g', 'CSP-i', 'gfound', 'rfound', 'ifound', 'zfound', 'gp1', 'rp1', 'ip1', 'zp1', 'ps1_r', 'ps1_i', 'ps1_y', 'ps1_z', 'ps1::g', 'ps1::r', 'ps1::i', 'ps1::z', 'u', 'g', 'r', 'i', 'r4sh', 'i4sh', 'rk2', 'ik2','rk1','ik1', 'cfa4-n', 'cfa4-o', 'cfa4-r', 'cfa4-s', 'ztfg', 'ztfr', 'ztfi', 'NLB_u', 'NLB_g', 'NLB_r', 'NLB_i']
#bd17_filt  = ['B4sh', 'V4sh', 'r4sh', 'i4sh', 'Bk2', 'Vk2', 'rk2', 'ik2', 'cfa4-l', 'cfa4-m', 'cfa4-n', 'cfa4-o', 'cfa4-p',  'cfa4-q', 'cfa4-r', 'cfa4-s']
bd17_filt = []
# repurpose the CfA filters 


errfloor = float(sys.argv[8])

#print(lcs)
#err_floor = float(sys.argv[2])#0.04
def conv_snana_sncosmo(lc, csp_ab_offset, ab_filt=ab_filt, vega_filt=vega_filt, bd17_filt=bd17_filt):
    """
    Input: lc in snana format
            AB offset dictionary
    Returns: lc table in sncosmo format

    It started as just a formatting function but now all the zeropoint conversions from different systems is here. 
    Not any "standard" system conversions, just conversions to either AB or BD17 if the data doesn't exist in one system
 
    """


    lc_sn_tab = Table()
    lc_sn_tab['time'] = lc['mjd']
    lc_sn_tab['band'] = lc['flt']
    lc_sn_tab['flux'] = lc['fluxcal']
    lc_sn_tab['flux_err'] = lc['fluxcalerr']
    lc_sn_tab['zp'] = lc['zptmag']
    zpsys_arr = []
    zp_arr =[]
    # getting the zeropoints and the system correct

    for ii, bval in enumerate(lc_sn_tab['band']):
        # if its not in a set of filters determined to be AB mag
        # or tied to a different standard like BD17 
        # then please set it to vega 

        if bval not in ab_filt and bval not in bd17_filt and bval not in csp_ab_offset.keys() and bval not in cfa_vegnat_offset.keys() and bval in csp_vegnat_offset.keys(): 
            vegnat_off = csp_vegnat_offset[bval]
            zp_arr.append(lc['zptmag'][ii] - vegnat_off)
            zpsys_arr.append('vega')

        elif bval not in ab_filt and bval not in bd17_filt and bval not in csp_ab_offset.keys() and bval not in csp_vegnat_offset.keys() and bval in cfa_vegnat_offset.keys(): 
            vegnat_off = cfa_vegnat_offset[bval]
            zp_arr.append(lc['zptmag'][ii] - vegnat_off)
            zpsys_arr.append('vega')
            
        elif bval not in ab_filt and bval not in bd17_filt and bval not in csp_ab_offset.keys(): 
            zp_arr.append(lc['zptmag'][ii])
            zpsys_arr.append('vega')
            
        # if its in a particular set of CSP filters which are in BD17
        # system
        elif bval in csp_ab_offset.keys() and bval not in cfa_ab_offset.keys() and bval in ab_filt:
            ab_off = csp_ab_offset[bval]
            zp_arr.append(lc['zptmag'][ii] + ab_off)
            zpsys_arr.append('ab')

        elif bval in cfa_ab_offset.keys() and bval not in csp_ab_offset.keys() and bval in ab_filt:
            ab_off = cfa_ab_offset[bval]
            zp_arr.append(lc['zptmag'][ii] + ab_off)
            zpsys_arr.append('ab')

        elif bval in csp_ab_offset.keys() and bval not in ab_filt:
            print("ERROR, ERROR, ERROR; something is wrong if the filter is in the correction directory but not AB list")
            sys.exit()

        elif bval in bd17_filt: 
            zp_arr.append(lc['zptmag'][ii])
            zpsys_arr.append('bd17')
        else:
            zp_arr.append(lc['zptmag'][ii])
            zpsys_arr.append('ab')


    lc_sn_tab['zp'] = zp_arr
    lc_sn_tab['zpsys'] = zpsys_arr#['ab' for ii in range(len(lc['zptmag']))]
    return lc_sn_tab

def offset_percent(data, model):
     
    fls = np.unique(data['band'])
    print(fls)
    dict_system = {}
    for fval in fls: 
        cond = data['band'] == fval
        mflux, mcov = model.bandfluxcov(fval, data['time'][cond], data['zp'][cond], data['zpsys'][cond])
        print(fval, "bloop")
        deltaf = data['flux'][cond] - mflux
        pull = deltaf / data['flux_err'][cond]
        dict_system[fval] = [len(deltaf[deltaf <= 0]), len(deltaf), np.median(pull)]
    return dict_system

if 'HubbleFlow' in lc_path:
    metafile = '../metafiles/PanthPlus_meta.txt'
    zindexx = 1
    str_tag = '_hf_'
elif 'calib' in lc_path:
    #metafile = '../metafiles/Calib_TRGB_set_meta.txt'
    metafile = '../metafiles/calib_new_zval.txt'
    #zindexx = 2
    zindexx = 1
    str_tag = '_trgb_calib_'
    
#print("Using metafile: ", metafile)
#z_file_vals = np.loadtxt(metafile, dtype=str)
filtopt = ['CSP-u', 'U4sh', 'Uk2','Uk1', 'u4sh', 'u', 'U', 'NLB_u', 'UVOT-U', 'UVOT-R', 'CSP-J', 'uk2', 'zfound', 'R4sh', 'NLB_g', 'J2m','H2m','Ks2m', 'CSP-Y', 'CSP-K', 'CSP-H', 'Us', 'CSP-Jrc2', 'CSP-Hrc2', 'J', 'H', 'K', 'Y', 'Jrc2', 'Hrc2', 'K_AND', 'J_AND', 'H_AND', 'Ydw', 'CSP-Ydw', 'CSP-y', "WHIRCH", "WHIRCJ", "H_P", "J_P", "K_P", "WHIRCK", 'ps1::z', 'ps1_z', 'zp1', 'CSP-j', 'CSP-h']
fitopt = True
#print(z_file_vals)

# only fit the bvr filter set 
bvr = sys.argv[2]
bvr_vals = ['BV', 'VR', 'BR', 'BVR', 'BVRI']
#if bvr: 
assert bvr in bvr_vals
plt_str = bvr
lcs = [val for val in lcs if 'ps1' not in val]
print(lcs)
# without the explicit cut, this will probably include ignoring the NIR and u-band anyways
# KEEP a clear  

## define the column names 
panth_shoes = np.loadtxt('../current_cosmo_sample/Pantheon+SH0ES.dat', dtype=str)
panth_cols = panth_shoes[0]
panth_vals = panth_shoes[1:]
print(panth_cols)

## define the 
x0_indexx = np.where(panth_shoes[0] == 'x0')[0][0]
x1_indexx = np.where(panth_shoes[0] == 'x1')[0][0]
c_indexx =  np.where(panth_shoes[0] == 'c')[0][0]
z_file_vals = np.loadtxt('../metafiles/calib_new_zval.txt', dtype=str)
# get what the ZPs are for the different SALT models 
if snmodel_str == 'dove': 
    dove_zp = pd.read_pickle('zeropoints_filters/zp_dovekie_direct.pkl')
    cfa_filt_map = pd.read_pickle('zeropoints_filters/cfa_filtermaps.pkl')
# this may not strictly be correct since the calibration error would 
# change with the SALT model but the closest thing to do for salt3 
# would be to continue with fragilistic
# since dovekie is an updated model anyways, I shouldn't be too bothered

elif snmodel_str == 'salt2' or snmodel_str == 'salt3': 
    dove_zp = pd.read_pickle('zeropoints_filters/zp_frag_direct.pkl')
    cfa_filt_map = pd.read_pickle('zeropoints_filters/cfa_filtermaps.pkl')
print(dove_zp)

#sys.exit()
if cov: 
    cov_str = 'WithCov'
else: 
    cov_str = 'NoCov'
outpath = '../outputs/plots/dovekie/'

cfa_conv = {'a':'u4sh', 'b':'B4sh', 'c':'V4sh', 'd':'r4sh', 
'e':'i4sh', 'f':'Uk1', 'g':'Bk1', 'h':'Vk1', 'i':'rk1', 'j':'ik1'}

# debugging description here: 
# this is where I am storing all the SNe that did not pass some cut and 
# therefore there is no endgame pretty plot 
not_worked_sne = []

# debug mode on for the four missing objects 
# this is when the fitter fails for specific objects and I only want 
# to find what is not working for them 
# its typically a smaller array / list of names to which lcs is truncated 
debug_mode = False
if debug_mode: 
    #cc = ['SN1991T', 'SN1990N', 'SN2020nlb','SN2021rhu']
    cc = ['2021J']
    lcs = [ii for ii in lcs if io.read_snana_lcfile(ii)[0]  in cc]
print("Starting the fitting part now")

outfitdir = '../outputs/fit_params/mwext/'
if 'hubble' in lcs[0] or 'Hubble' in lcs[0]: 
    outfitdir += '/Hubbleflow/'
    if not os.path.exists(outfitdir): 
        os.makedirs(outfitdir)
    # after the amount of grief it gave me to fit the CfA lightcurve 
    # It also wont override the CSP then
    if 'CfA' in lcs[0]: 
        outfitdir += '/CfA/'
        if not os.path.exists(outfitdir): 
            os.makedirs(outfitdir)

zptcorr = bool(sys.argv[9])
if zptcorr: 
    outfitdir += 'zptcorr/'
    if not os.path.exists(outfitdir): 
        os.makedirs(outfitdir)
fit_count = 0 

dove_filts = ['CSP-V', 'CSP-B', 'CSP-m', 'CSP-n', 'CSP-o', 'cfa4-p', 'cfa4-q', 'cfa4-r', 'cfa4-s', 'cfa4-l', 'cfa4-m', 'cfa4-n', 'cfa4-o', 'B4sh', 'Bk2']
# define the uniform errorfloor
st = time()
print("outfits stored in:", outfitdir)
print(lcs)
# fitting loop begins below 
#lcs = [ii for ii in lcs if ] 
for fname in lcs: 
    print(fname)
    sn, lc = io.read_snana_lcfile(fname)
    # 
    print("The SN value is: ", sn)
    #if not 'SN' in sn: 
    #    sn = 'SN' + sn

    if not 'flt' in lc.keys():
        lc['flt'] = lc['band']

    # bespoke modelling of the filters for SN
    # depending on the fname 
    if  '2020nvb' in fname or '2021pit' in fname: 
        lc['flt'] = ['UVOT-'+ii for ii in lc['flt']]
        for fval3 in ['UVOT-X', 'UVOT-N', 'UVOT-W', 'UVOT-x', 'UVOT-n', 'UVOT-w']:
            lc = lc[lc['flt'] != fval3]
    if '2021J' in fname: 
        lc['flt'] = [ii+'found' for ii in lc['flt']]
    # should 2007sr be added too? 
    if '2007af' in fname or '2007on' in fname or '2011iv' in fname or '2007sr' in fname:# or '2015F' in fname: 
        lc['flt'] = ['CSP-'+ii for ii in lc['flt']]
    if '2006dd' in fname:
        bandvals = []
        for ii in lc['flt']: 
            if 'AND' in ii: 
                bandvals.append(ii)
            else:
                bandvals.append('CSP-'+ii)
        lc['flt'] = bandvals
    if '2015F' in fname or '2012fr' in fname: 
        bandvals = []
        for ii in lc['flt']:
            if ii == 'V': 
                bandvals.append('CSP-n')
            else:
                bandvals.append('CSP-'+ii)    
        lc['flt'] = bandvals #['CSP-'+ii for ii in lc['flt']]
    if '2017erp' in fname or '2011by' in fname or '2013dy' in fname:
        print(np.unique(lc['flt']))  
        lc['flt'] = [filter_keys[key] for key in lc['flt']]
        print('the filter transform seems to work for', sn)
    try:
        zval = float(z_file_vals[z_file_vals[:,0] == sn][0][zindexx])
    except: 
        # the SN string being further cast as a string is intentional
        # some SN names are just numbers which need changing

        if 'SN'+str(sn) in z_file_vals[:,0]:
            zval = float(z_file_vals[z_file_vals[:,0] == 'SN'+sn][0][zindexx])
        else:
            if 'REDSHIFT_HELIO' in lc.meta.keys():
                zval = lc.meta['REDSHIFT_HELIO']
            elif 'REDSHIFT_FINAL' in lc.meta.keys():
                zval = lc.meta['REDSHIFT_FINAL']
    if 'Foundation' in fname: 
            # rewrite the string to the value that is in the 
            # bandpass registry 
            lc['flt'] = [ii+'found' for ii in lc['flt']]
            outdir = '../outputs/plots/Hubbleflow/Found/'
            if not os.path.exists(outdir):
                os.makedirs(outdir)

    elif 'CSPDR3' in fname: 
            lc['flt'] = ['CSP-'+ii for ii in lc['flt']]
            outdir = '../outputs/plots/Hubbleflow/CSP/'
            if not os.path.exists(outdir):
                os.makedirs(outdir)

    elif 'CfA' in fname:
            filt_arr = []
            for ii2 in lc['flt']: 
                if ii2 in cfa_conv.keys():
                    filt_arr.append(cfa_conv[ii2])
                elif 'CfA4' in fname: 
                    filt_arr.append('cfa4-'+ii2)
                else:
                    filt_arr.append(ii2)
            lc['flt'] = filt_arr
            outdir = '../outputs/plots/Hubbleflow/CfA/'
            if not os.path.exists(outdir):
                os.makedirs(outdir)
    if fitopt: 
            for fval in filtopt: 
                lc = lc[lc['flt'] != fval]
            # only apply BVR to the hubble flow with the same filter region 
            # i.e. with BVRi lightcurves not griz 
            # so this restricts tests to CfA + CSP but that is a sufficiently large sample size
            # for each pairwise inclusion or exclusion define all the strings which correspond to 
            # a given waveband 
            if bvr == 'BVR': 
                fls = np.unique(lc['flt'])
                for fval2 in fls: 
                    if ('i' in fval2 and 'nickel' not in fval2) or ('I' in fval2 and 'KAIT' not in fval2 and 'nickel' not in fval2) or 'nickel2-P' in fval2 or 'nickel1-L' in fval2 or 'KAIT1-d' in fval2 or 'ASASSN-d' in fval2 or 'KAIT4-H' in fval2 or 'cfa4-s' in fval2 or 'cfa4-o' in fval2: 
                        lc = lc[lc['flt'] != fval2]
                #if snmodel_str == 'salt2': 
                #        lc = lc[lc['flt'] != 'r4sh']
                #        lc = lc[lc['flt'] != 'R4sh']
            elif bvr == 'BV': 
                fls = np.unique(lc['flt'])
                for fval2 in fls: 
                    if 'i' in fval2 or 'I' in fval2 or 'r' in fval2  or 'R' in fval2 or 'KAIT4-G' in fval2 or 'nickel1-K' in fval2 or 'KAIT3-C' in fval2 or 'nickel2-O' in fval2: 
                        lc = lc[lc['flt'] != fval2]

            elif bvr == 'VR' and 'Foundation' not in fname: 
                for fval2 in np.unique(lc['flt']): 
                    if 'i' in fval2 or 'I' in fval2 or 'B' in fval2  or 'b' in fval2 or 'cfa4-l' in fval2 or 'cfa4-p' in fval2 or 'KAIT4-E' in fval2 or 'nickel1-I' in fval2 or 'KAIT3-A' in fval2 or 'nickel2-M' in fval2: 
                        lc = lc[lc['flt'] != fval2]
            elif bvr == 'BR' and 'Foundation' not in fname: 
                for fval2 in np.unique(lc['flt']): 
                    if 'i' in fval2 or 'I' in fval2 or 'V' in fval2  or 'v' in fval2 or 'cfa4-m' in fval2 or 'cfa4-q' in fval2 or 'CSP-n' in fval2 or 'CSP-o' in fval2 or 'CSP-m' in fval2 or 'KAIT4-F' in fval2 or 'nickel1-J' in fval2 or 'KAIT3-B' in fval2 or 'nickel2-N' in fval2:  
                        lc = lc[lc['flt'] != fval2]
    #print(lc['band'])
    lc_sn = conv_snana_sncosmo(lc, csp_ab_offset) 
    if snmodel_str == 'dove':
        lc_sn['band'] = [x+'_dove' if x in dove_filts else x for x in lc_sn['band']]
    print(np.unique(lc_sn['band']), np.unique(lc['flt']))
        
    # add the error floor
    # if the error floor is > 1 then divide the flux error
    # else add in quadrature
    if errfloor >= 1: 
        lc_sn['flux_err'] /= errfloor #np.sqrt(lc_sn['flux_err'] ** 2. + (errfloor * lc_sn['flux']) ** 2.)
    
    else: 
        lc_sn['flux_err'] = np.sqrt(lc_sn['flux_err'] ** 2. + (errfloor * lc_sn['flux']) ** 2.)
    
    #print(np.unique(lc_sn['band']))
    model['z'] = zval
    print('The redshift of SN, ',sn, ' is ', zval)
    param_dict = {}
    # get the ebv 
    if str(sn) in panth_vals[:,0] or "SN"+str(sn) in panth_vals[:,0] or str(sn[2:]) in panth_vals[:,0]:
        if str(sn) in panth_vals[:,0]:
            sn_cols = panth_vals[panth_vals[:,0] == str(sn)]
        elif str(sn[2:]) in panth_vals[:,0]:
            sn_cols = panth_vals[panth_vals[:,0] == str(sn[2:])]
        else: 
            sn_cols = panth_vals[panth_vals[:,0] == "SN"+str(sn)]
        #print(sn_cols)
        x0val = float(sn_cols[0][x0_indexx])
        x1val = float(sn_cols[0][x1_indexx])
        cval = float(sn_cols[0][c_indexx])
        param_dict['z'] = zval
        param_dict['x0'] = x0val
        param_dict['x1'] = x1val
        param_dict['c'] = cval 
        param_dict['MWRv'] = 3.1
    # I compute the zeropoint offsets in any case for each of the filters in the fset in
    # either frag or dove. this gets saved as a column in the astropy table 

    zptcorr_arr = []
    for fval in lc_sn['band']: 
    #print(fval)

        #if fval in cfa_filt_map.keys():
        #    fout = cfa_filt_map[fval]
        #else:
        #    fout = fval 
        #print(fout)
        #if fout in dove_zp.keys():
        #    zpoff = dove_zp[fout]
        #elif fout.upper() in dove_zp.keys():
        #    zpoff = dove_zp[fout.upper()]
        if fval in dove_zp.keys(): 
            zpoff = dove_zp[fval]
        elif fval.upper() in dove_zp.keys(): 
            zpoff = dove_zp[fval.upper()]
        else:
            zpoff = 0
            print("filter value: ", fval, " isn't in the pickle")
        zptcorr_arr.append(float(zpoff))
    lc_sn['zptcorr'] = zptcorr_arr
    #print(np.unique(zptcorr_arr), np.unique(lc_sn['band']))
    if zptcorr:  
        lc_sn['zp'] -= lc_sn['zptcorr']
    # alot of this is about the string of the SN name and if it has the tag "SN" in it
    #if 'SN' in str(sn) or 'PS' in str(sn) or 'MASTER' in str(sn) or 'AT' in str(sn) or 'CSS' in str(sn) or 'Gaia' in str(sn) or 'PTF' in str(sn):
    #    sim_query = Simbad.query_object(str(sn))
    #else:
    #    sim_query = Simbad.query_object("SN" + str(sn))
    
    try: 
        ra = lc.meta['RA']

        if 'DECL' in lc.meta.keys(): 
            dec = lc.meta['DECL']
        elif 'DEC' in lc.meta.keys(): 
            dec = lc.meta['DEC']
        
        #print("Sim query done", sim_query)
        #if len(sim_query['ra']) > 0:
        #    if dustmap_val == 'Bayestar':
        #        coord = SkyCoord(sim_query['ra'][0], sim_query['dec'][0], distance= 500 *u.pc, frame='icrs', unit=(u.deg, u.deg))
        
        #    else:
        #        coord = SkyCoord(sim_query['ra'][0], sim_query['dec'][0], frame='icrs', unit=(u.deg, u.deg))
        #else: 
        #    ra = lc.meta['RA']
        #    dec = lc.meta['DECL']
        coord = SkyCoord(ra, dec, frame='icrs', unit=(u.deg, u.deg))
        # currently I am not setting anything beforehand because I wouldn't want 
        # to mess up the different ways in which the dustmaps and sfdmap packages 
        # take in the coordinates and setup the classes 
        # the sfdmap takes (ra, dec) where dustmaps takes the whole instantiated skycoord
        # since this script is only changing two main things, i.e. the RV and the E(B-V) 
        # it should be fine to use if conditional as more maps are added
        
        if dustmap_val == 'SF11': 
            ebv = dustmaps.ebv(coord.ra.deg, coord.dec.deg)
            print(ebv)
        elif dustmap_val == 'Planck': 
            ebv = PlanckDust(coord)
        elif dustmap_val == 'Leike2020':
            ebv = LeikeDust(coord)
        elif dustmap_val == 'Bayestar':
            # whats the mode = for? what are the different values
            ebv = BayestarDust(coord)
        elif dustmap_val == 'gaia': 
            ebv = GaiaDust(coord)

        model['MWebv'] = ebv
        param_dict['MWebv'] = ebv
        print("Made it past ebv")
        # this is the fitting section (the "business" end)
        res, fitted_model = sncosmo.fit_lc(lc_sn, model, ['t0', 'x0', 'x1', 'c'],
     modelcov=False)
        print("First Fit")
        cond = (lc_sn['time'] >= res.parameters[1] - 10) & (lc_sn['time'] <= res.parameters[1]+40)
        lc_phasetrimmed = lc_sn[cond]
        if fitter_val == 'minuit':
            res_fin, fitted_model_fin = sncosmo.fit_lc(lc_phasetrimmed, model, ['t0', 'x0', 'x1', 'c'],
     modelcov=cov)
        elif fitter_val == 'mcmc':
            bounds_mcmc = {'t0':(res.parameters[1] - 100, res.parameters[1] +100), 'x0':(1e-11, 1.), 
            'x1':(-5, 5), 'c':(-0.5, 2.)}
            res_fin, fitted_model_fin = sncosmo.mcmc_lc(lc_phasetrimmed, model, ['t0', 'x0', 'x1', 'c'],
     bounds=bounds_mcmc, nwalkers=100, nburn=500, nsamples=5000)
        #system_filt = offset_percent(lc_phasetrimmed, fitted_model_fin)
        
        #res_fin['system_filt'] = system_filt
        print(' Filt System done ')

        res_fin['dustmap'] = dustmap_val
        res_fin['dustlaw'] = dustmod
        pd.to_pickle(res_fin, outfitdir+sn+str_tag+snmodel_str+'_'+cov_str+'_'+fitter_val+'_floor'+str(errfloor)+'_'+dustmod+'_'+dustmap_val+'map_'+plt_str+'.pkl')
        print("Fitting is done lets see plotting")
        

    #   plot_mag_models(lc_phasetrimmed, fitted_model_fin, snmodel, sn, param_dict, snmodel_str+'_'+cov_str+'_'+plt_str, reset_model=False, outpath=outpath)
        #plot_flux_sncosmo_models(lc_phasetrimmed, fitted_model_fin, snmodel, sn, param_dict, snmodel_str+'_'+cov_str+'_'+plt_str, reset_model=False, outpath=outpath)
        #plt.cla()
        if 'calib' in lc_path: 
            plot_output_str = '../outputs/plots/calibrators/mwext/'
        else:
            plot_output_str = '../outputs/plots/mwext/'
        plot_output = os.path.join(plot_output_str, snmodel_str)
        if not os.path.exists(plot_output):
            os.makedirs(plot_output)
        sncosmo.plot_lc(lc_phasetrimmed, model=fitted_model_fin, show_model_params=False, fname=plot_output+'/'+sn+'_'+snmodel_str+'_'+cov_str+'_'+fitter_val+'_floor'+str(errfloor)+'_'+dustmod+'_'+dustmap_val+'map_'+plt_str+'.pdf')
        print("A new file has been written to the plot")
        fit_count += 1
    except: 
        print("Didnt get to the end: ", sn)
        not_worked_sne.append(sn)
        plt.cla()

end = time()
duration = (st - end) / 60.
print("Total time taken is: ", abs(round(duration, 3)), " minutes")
print("The total number of objects fitted is ", fit_count)
print("SN Failures (but in their own special way) are: ", not_worked_sne)
    #print(lc_sn)
    #print(sn)
