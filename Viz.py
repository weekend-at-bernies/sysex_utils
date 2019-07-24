#!/usr/bin/python

# REQUIREMENTS:
#
# https://bitbucket.org/techtonik/hexdump/ 
# $ pip install hexdump
#
#

import os
import sys
import optparse
import rolandjx8p_syx
import yamahadx7_syx
import yamahatx802_syx
import binascii
# Only use hexdump for python 2 (at the moment)
if not sys.version_info >= (3,0):
    import hexdump
import hashlib
import numpy as np

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def printHelpAndExit():
    parser.print_help()
    exit(-1)

#################################################################################################################

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", help="directory with sysex (.syx) files", dest="inputdir",  metavar="<input directory>")
    (opts, args) = parser.parse_args()

if (opts.inputdir is None):
    print("Error: <input file> not specified\n")
    printHelpAndExit()


data_list = []
count = 0
for filename in os.listdir(opts.inputdir):
    if filename.endswith(".patch") or filename.endswith(".syx"):
        try:
            f = open(os.path.join(opts.inputdir, filename),"rb")
            data = f.read()
            f.close()
        except IOError:
            print("Error: could not open: %s\n"%(opts.inputdir))
            exit(-1)

        if len(data) != 128:
            print('len(data)',len(data))

        if len(data) == 4104:
            syx = yamahadx7_syx.SysEx(data)
            print(syx.prettyPrint())
        elif len(data) == 128:
            patch = yamahadx7_syx.Patch(data)
            #print(patch.prettyPrint())
            patchData = patch.listData()
            #print(patchData)
            if len(patchData) == 88:
                data_list.append([float(i) for i in patchData])
            else:
                print('Error: unexpected number of elements in patch:',len(patchData))
                exit(-1)
        else:
            print("Error: unknown file type: %s"%(opts.inputdir))
        count += 1

data_array = np.array(data_list)
print('data_array.shape',data_array.shape)

exit(0)


