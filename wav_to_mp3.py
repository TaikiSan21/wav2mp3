# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 15:44:19 2022
Downsample and create mp3
@author: tnsak
"""
import scipy.signal as signal
from scipy.io import wavfile
import os
import numpy as np
from pydub import AudioSegment
from pydub import effects
import argparse
from tqdm import trange
import yaml
import re

def do_decimate(wav, srFrom, srTo):
    # decimation factor can be non-int
    q = srFrom / srTo
    # do order-8 cheby filter anti-alias
    sos = signal.cheby1(8, .05, .8/q, output='sos')
    filt_wav = signal.sosfiltfilt(sos, wav)
    # get every q-th item from original wav
    deci_seq = np.array([x * q for x in range(0, np.int32(len(wav)/q))]).astype(np.int32)
    return filt_wav[deci_seq]

def do_filt_deci(file, deci=8000, low=100, high=6000, out_dir=''):
    sr, wav = wavfile.read(file)
    sos = signal.butter(4, low, btype='high', fs=sr, output='sos')
    wav = signal.sosfiltfilt(sos, wav)
    if high > deci:
        high = deci
    if high < deci:
        sos = signal.butter(4, high, btype='low', fs=sr, output='sos')
        wav = signal.sosfiltfilt(sos, wav)
    
    wav = do_decimate(wav, sr, deci)
    fname = 'Deci'+str(deci)+'_'+os.path.basename(file)
    fname = os.path.join(out_dir, fname)
    wavfile.write(fname, deci, wav.astype(np.int16))
    return fname
    
def normalize_file(file, normtype='fixed', amount=5):
    wav = AudioSegment.from_file(file)
    match normtype:
        case 'fixed':
            wav = wav.apply_gain(amount)
        case 'max':
            wav = effects.normalize(wav, amount)
    
    return wav

def main():
    # -*- coding: utf-8 -*-
    """
    script for downsampling high bandwidth files and writing
    decimated MP3s
    Change parameters in config.yaml 
    """
    # setting up command line arugment parser 
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', help='Path to config file', default='config.yaml')
    args = parser.parse_args()
    
    # load config
    print(f'Using config "{args.config}"')
    cfg = yaml.safe_load(open(args.config, 'r'))
    # get only .wav files from folder
    in_files = [os.path.join(cfg['in_dir'], x) 
                for x in os.listdir(cfg['in_dir']) 
                if re.search('\\.wav$', x)]
    
    # If no out specified will put in "in" folder. Not recommended.
    wav_dir = cfg['out_wav'] if cfg['out_wav'] else cfg['in_dir']
    os.makedirs(wav_dir, exist_ok=True)
    mp3_dir = cfg['out_mp3'] if cfg['out_mp3'] else cfg['in_dir']
    os.makedirs(mp3_dir, exist_ok=True)
    out_mp3 = []
    out_wav = []
    pb = trange(len(in_files))
    for f in in_files:
        this_file = do_filt_deci(f, 
                                 cfg['mp3_sr_hz'], 
                                 cfg['low_filt_hz'], 
                                 cfg['high_filt_hz'],
                                 wav_dir)
        out_wav.append(this_file)
        aud_seg = normalize_file(this_file, cfg['norm_type'], cfg['norm_value'])
        this_out = re.sub('wav$', 'mp3', os.path.basename(this_file))
        this_out = os.path.join(mp3_dir, this_out)
        outf = aud_seg.export(this_out, format='mp3')
        outf.close()
        out_mp3.append(this_out)
        if cfg['delete_wav']:
            os.remove(this_file)
        pb.update(1)
    if cfg['delete_wav'] and cfg['']:
        os.rmdir(cfg['out_wav'])
    return out_wav, out_mp3

# this happens when you call wav_to_mp3.py from command line
if __name__ == '__main__':
    main()
