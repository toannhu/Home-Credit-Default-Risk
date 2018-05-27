#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:45:03 2018

@author: kazuki.onodera
"""

import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool
from glob import glob
import utils
utils.start(__file__)
#==============================================================================
KEY = 'SK_ID_CURR'
PREF = 'pos'

NTHREAD = 2

col_num = ['MONTHS_BALANCE', 'CNT_INSTALMENT', 'CNT_INSTALMENT_FUTURE',
           'SK_DPD', 'SK_DPD_DEF']

col_cat = ['NAME_CONTRACT_STATUS']

col_group = ['SK_ID_PREV', 'NAME_CONTRACT_STATUS']

# =============================================================================
# feature
# =============================================================================
pos = utils.read_pickles('../data/POS_CASH_balance')
base = pos[[KEY]].drop_duplicates().set_index(KEY)

#### newest ####
for T in range(-1, -6, -1):
    print(T)
    pos_ = pos[pos['MONTHS_BALANCE']==T]
    
    gr = pos_.groupby(KEY)
    base[f'pos-T{T}_size'] = gr.size()
    base[f'pos-T{T}_CNT_INSTALMENT_FUTURE_sum'] = gr['CNT_INSTALMENT_FUTURE'].sum()
    base[f'pos-T{T}_CNT_INSTALMENT_sum']        = gr['CNT_INSTALMENT'].sum()
    base[f'pos-T{T}_CNT_INSTALMENT_ratio'] = base[f'pos-T{T}_CNT_INSTALMENT_FUTURE_sum'] / base[f'pos-T{T}_CNT_INSTALMENT_sum']
    
    c1 = 'NAME_CONTRACT_STATUS'
    df = pd.crosstab(pos_[KEY], pos_[c1])
    df.columns = [f'pos-T{T}_{c2.replace(" ", "-")}_sum' for c2 in df.columns]
    col = df.columns.tolist()
    base = pd.concat([base, df], axis=1)
    base[col] = base[col].fillna(-1)
    
    base['pos-T{T}_SK_DPD_sum']           = gr['SK_DPD'].sum()
    base['pos-T{T}_SK_DPD_DEF_sum']       = gr['SK_DPD_DEF'].sum()
    base['pos-T{T}_CNT_INSTALMENT_ratio'] = base['pos-T{T}_SK_DPD_sum'] / base['pos-T{T}_SK_DPD_DEF_sum']
    
    base.fillna(-1, inplace=True)

#### comp MONTHS_BALANCE ####
comp = pos[pos['NAME_CONTRACT_STATUS']=='Completed']
df = comp.sort_values(['SK_ID_CURR', 'MONTHS_BALANCE']).drop_duplicates('SK_ID_CURR', keep='last')
df.set_index('SK_ID_CURR', inplace=True)
df = df[['MONTHS_BALANCE']]
base['pos-comp_last_month'] = df
base['pos-comp_cnt'] = comp.groupby(KEY).size()



def nunique(x):
    return len(set(x))

def multi_gr2(k):
    gr2 = pos.groupby([KEY, k])
    gc.collect()
    print(k)
    keyname = 'gby-'+'-'.join([KEY, k])
    # size
    gr1 = gr2.size().groupby(KEY)
    name = f'{PREF}_{keyname}_size'
    base[f'{name}_min']  = gr1.min()
    base[f'{name}_max']  = gr1.max()
    base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
    base[f'{name}_mean'] = gr1.mean()
    base[f'{name}_std']  = gr1.std()
    base[f'{name}_sum']  = gr1.sum()
    base[f'{name}_nunique']     = gr1.size()
    for v in col_num:
        
        # min
        gr1 = gr2[v].min().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_min'
        base[f'{name}_max']     = gr1.max()
        base[f'{name}_mean']    = gr1.mean()
        base[f'{name}_std']     = gr1.std()
        base[f'{name}_sum']     = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # max
        gr1 = gr2[v].max().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_max'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # mean
        gr1 = gr2[v].mean().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_mean'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # std
        gr1 = gr2[v].std().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_std'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # sum
        gr1 = gr2[v].sum().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_sum'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_nunique'] = gr1.apply(nunique)
    base.to_pickle(f'../data/tmp_{PREF}{k}.p')
    
# =============================================================================
# gr2
# =============================================================================
pool = Pool(NTHREAD)
callback = pool.map(multi_gr2, col_group)
pool.close()

# =============================================================================
# gr1
# =============================================================================
gr = pos.groupby(KEY)

# stats
keyname = 'gby-'+KEY
for c in col_num:
    gc.collect()
    print(c)
    base[f'{PREF}_{keyname}_{c}_min'] = gr[c].min()
    base[f'{PREF}_{keyname}_{c}_max'] = gr[c].max()
    base[f'{PREF}_{keyname}_{c}_max-min'] = base[f'{PREF}_{keyname}_{c}_max'] - base[f'{PREF}_{keyname}_{c}_min']
    base[f'{PREF}_{keyname}_{c}_mean'] = gr[c].mean()
    base[f'{PREF}_{keyname}_{c}_std'] = gr[c].std()
    base[f'{PREF}_{keyname}_{c}_sum'] = gr[c].sum()
    base[f'{PREF}_{keyname}_{c}_nunique'] = gr[c].apply(nunique)

    
# =============================================================================
# cat
# =============================================================================
for c1 in col_cat:
    gc.collect()
    print(c1)
    df = pd.crosstab(pos[KEY], pos[c1])
    df.columns = [f'{PREF}_{c1}_{c2.replace(" ", "-")}_sum' for c2 in df.columns]
    col = df.columns.tolist()
    base = pd.concat([base, df], axis=1)
    base[col] = base[col].fillna(-1)


# =============================================================================
# merge
# =============================================================================
df = pd.concat([ pd.read_pickle(f) for f in sorted(glob(f'../data/tmp_{PREF}*.p'))], axis=1)
base = pd.concat([base, df], axis=1)
base.reset_index(inplace=True)
del df; gc.collect()

train = utils.load_train([KEY])
train = pd.merge(train, base, on=KEY, how='left').drop(KEY, axis=1)


test = utils.load_test([KEY])
test = pd.merge(test, base, on=KEY, how='left').drop(KEY, axis=1)

utils.to_pickles(train, '../data/104_train', utils.SPLIT_SIZE)
utils.to_pickles(test,  '../data/104_test',  utils.SPLIT_SIZE)






#==============================================================================
utils.end(__file__)

