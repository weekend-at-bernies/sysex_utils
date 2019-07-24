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
import yamahadx7_syx
import binascii
#import hexdump
import hashlib
from glob import glob
 
# DESCRIPTION HERE:
# Takes input directory, recursively looks for ALL .syx, and extracts UNIQUE .patch files to output directory
# Run it 



def printHelpAndExit():
    parser.print_help()
    exit(-1)

#################################################################################################################

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", help="input directory (default: current)", dest="inputdir",  metavar="<directory>")
    parser.add_option("-x", help="don't ask (just do)", action="store_true", dest="dontask",  default=False)
    (opts, args) = parser.parse_args()

if (opts.inputdir is None):
    print("Error: <directory> not specified\n")
    printHelpAndExit()

if not os.path.isdir(opts.inputdir):
    print("Error: input <directory> does not exist: %s\n"%(opts.inputdir))
    printHelpAndExit()


# Enumerate all .patch filenames below input directory
fn_l = [y for x in os.walk(opts.inputdir) for y in glob(os.path.join(x[0], '*.patch'))]
for fn in fn_l:
    #print fn
    try:
        f1 = open(fn, "rb")
        data = f1.read()
        f1.close()
        patch = yamahadx7_syx.Patch(data) 
 
        if patch.isNameUTF8():
            print("%s"%(patch.get_name()))
            
    except AssertionError as e:
        print(str(e))
        print("WARNING: could not process patch file: %s (skipping!)\n"%(fn))
        continue 

    except IOError:
        print("Error: could not open: %s\n"%(fn))
        exit(-1)


exit(0)


