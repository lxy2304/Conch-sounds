
from numpy import log10,zeros,abs,arange, hanning, pad, spacing, ceil, log, floor
from numpy.fft import fft

import librosa

from acousticsim.representations.base import Representation
from .helper import preemphasize


def signal_to_powerspec(signal, sr, win_len, time_step, alpha=0.97):
    x = preemphasize(signal, alpha)

    nperseg = int(win_len * sr)
    if nperseg % 2 != 0:
        nperseg -= 1

    nperstep = int(time_step*sr)
    nfft = int(2**(ceil(log(nperseg)/log(2))))
    window = hanning(nperseg+2)[1:nperseg+1]
    halfperseg = int(nperseg/2)
    indices = arange(halfperseg, x.shape[0] - (halfperseg + 1), nperstep)
    num_frames = len(indices)

    pspec = {}
    for i in range(num_frames):
        X = x[indices[i] - halfperseg:indices[i] + halfperseg]
        X = X * window
        fx = fft(X, n = nfft)
        power = abs(fx[:int(nfft/2)+1])**2
        pspec[indices[i] / sr] = power
    return pspec
    pass


def file_to_powerspec(file_path, win_len, time_step, alpha = 0.97):
    signal, sr = librosa.load(file_path, sr=None, mono=False)

    output = signal_to_powerspec(signal, sr, win_len, time_step, alpha)
    return output