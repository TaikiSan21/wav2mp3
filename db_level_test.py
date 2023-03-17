# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 10:25:00 2023
db test
@author: tnsak
"""
import os
from pydub import AudioSegment
from pydub import effects

folder = 'CCES_010_Add10dB'
# folder = 'louder'
files_mp3 = [os.path.join(folder, x) for x in os.listdir(folder) if 'mp3' in x]
files_png = [os.path.join(folder, x) for x in os.listdir(folder) if 'png' in x]

#%%
aseg = AudioSegment.from_file(files_mp3[0])

#%%
db_dict_orig = {'db': [],
           'db_max': []}
for x in files_mp3:
    aseg = AudioSegment.from_file(x)
    db_dict_orig['db'].append(aseg.dBFS)
    db_dict_orig['db_max'].append(aseg.max_dBFS)


#%%
import matplotlib.pyplot as plt
plt.plot(db_dict_orig['db'], 'b',
         db_dict_orig['db_max'], 'r')

#%%
import pandas as pd
df = pd.DataFrame(db_dict)
df['file'] = files_mp3
#%%
from PIL import Image, ImageDraw
import numpy as np

img = Image.open(files_png[0])
idraw = ImageDraw.Draw(img)
idraw.text((40, 40), 'DB: ' + str(np.round(db_dict['db'][0], 2)))
img.show()

#%%
ix = 0
img = plt.imread(files_png[ix])
fig, ax = plt.subplots()
ax.imshow(img)
ax.text(60, 60, 'DB: ' + str(np.round(db_dict['db'][ix], 2)), c='w')
ax.axis('off')
#%%
for (ix, (wav, img)) in enumerate(zip(files_mp3, files_png)):
    print(wav)
    print(img)
    print(ix)
#%% plotter fun
def plot_db(folder, ncol=10, n=None, file=None):
    files_mp3 = [os.path.join(folder, x) for x in os.listdir(folder) if 'mp3' in x]
    files_png = [os.path.join(folder, x) for x in os.listdir(folder) if 'png' in x]
    if n != None:
        files_mp3 = files_mp3[0:n]
        files_png = files_png[0:n]
    
    nrow = int(np.ceil(len(files_png)/ncol))
    mydpi = 96
    fig, ax = plt.subplots(nrow, ncol, 
                           figsize=(ncol * 1400/mydpi,
                                    nrow * 800/mydpi),
                           dpi=mydpi)
    
    for (ix, (wav, img)) in enumerate(zip(files_mp3, files_png)):
        aseg = AudioSegment.from_file(wav)
        row = int(np.floor(ix / ncol))
        col = ix % ncol
        ax[row, col].imshow(plt.imread(img))
        ax[row, col].axis('off')
        db_text = (f'DB: {np.round(aseg.dBFS, 2)}, '
                  f'DBMax: {np.round(aseg.max_dBFS, 2)}')
        ax[row, col].text(60, 50, s=db_text, c='w', size=30)
        ax[row, col].text(60, 90, s=wav, c='w', size=25)
        ax[row, col].set_xticks([])
        ax[row, col].set_yticks([])
    fig.tight_layout(pad=.01)
    if file != None:
        fig.savefig(file)
    
#%%
plot_db(folder,ncol=5, file='AllDb.png')
#%%
'''
lowest db is -63
highest is -47, still on quiet side but can hear with loud volume
probably test at +25 with cutoff of -40
'''
#%%
gain = 25
x = -80
thresh = -40
x + np.min([thresh - x, gain])
def gain_to_thresh(x, gain, thresh=-40):
    add = np.min([thresh - x.dBFS, gain])
    x = x.apply_gain(add)
    return x

gain_to_thresh(aseg, 15).dBFS
#%%
folder = 'CCES_010_Add10dB'
files = [x for x in os.listdir(folder) if 'mp3' in x]
out_folder = 'louder'
gain = 20 # add 10 to this for actual
thresh = -35

db_dict = {'db': [],
           'db_max': []}

for f in files:
    aseg = AudioSegment.from_file(os.path.join(folder, f))
    aseg = gain_to_thresh(aseg, gain, thresh)
    db_dict['db'].append(aseg.dBFS)
    db_dict['db_max'].append(aseg.max_dBFS)
    outf = aseg.export(os.path.join(out_folder, f), format='mp3')
    outf.close()


plt.plot(db_dict['db'], 'b',
         db_dict_orig['db'], '--b', 
         db_dict['db_max'], 'r',
         db_dict_orig['db_max'], '--r')

df = pd.DataFrame(db_dict)
df['file'] = files