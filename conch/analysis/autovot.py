from .functions import BaseAnalysisFunction
import wave
import subprocess
import textgrid 
import os
import tempfile

class MeasureVOTPretrained(object):
    def __init__(self, autovot_binaries_path=None, classifier_to_use=None, min_vot_length=15, max_vot_length=250):
        if autovot_binaries_path is None:
            self.autovot_binaries_path = '/home/michael/Honours-Thesis/autovot/autovot/bin/auto_vot_decode.py'
        if classifier_to_use is None:
            self.classifier_to_use = '/home/michael/Honours-Thesis/autovot/experiments/models/bb_jasa.classifier'
        self.min_vot_length = min_vot_length
        self.max_vot_length = max_vot_length

    def __call__(self, segment):
        file_path = segment["file_path"]
        begin = segment["begin"]
        end = segment["end"]
        vot_marks = segment["vot_marks"]
        grid = textgrid.TextGrid(maxTime=end)
        vot_tier = textgrid.IntervalTier(name='vot', maxTime=end)
        for (vot_begin, vot_end) in vot_marks:
            vot_tier.add(vot_begin, vot_end, 'vot')
        grid.append(vot_tier)
        with tempfile.TemporaryDirectory() as tmpdirname:
            grid_path = "{}/file.TextGrid".format(tmpdirname)
            csv_path = "{}/file.csv".format(tmpdirname)
            wav_filenames = "{}/wavs.txt".format(tmpdirname)
            textgrid_filenames = "{}/textgrids.txt".format(tmpdirname)

            with open(wav_filenames, 'w') as f:
                f.write("{}\n".format(file_path))

            with open(textgrid_filenames, 'w') as f:
                f.write("{}\n".format(grid_path))

            grid.write(grid_path)
            subprocess.run([self.autovot_binaries_path, wav_filenames, textgrid_filenames, self.classifier_to_use, '--vot_tier', 'vot', '--vot_mark', 'vot', '--csv_file', csv_path, "--min_vot_length", str(self.min_vot_length), "--max_vot_length", str(self.max_vot_length)])
            with open(csv_path, "r") as f: 
                f.readline()
                _, time, vot, confidence = f.readline().split(',')
            return (time, vot)

class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, autovot_binaries_path=None, classifier_to_use=None, min_vot_length=15, max_vot_length=250, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained(autovot_binaries_path=autovot_binaries_path, classifier_to_use=classifier_to_use, min_vot_length=min_vot_length, max_vot_length=max_vot_length)
        self.requires_file = True
        self.uses_segments = True
        self.requires_segment_as_arg = True
