#!/usr/bin/python

# REQUIREMENTS:
# $ pip install hexdump

import os
import sys
import optparse
import rolandjx8p_syx
import yamahadx7_syx
import binascii
import hexdump
 


def printHelpAndExit():
    parser.print_help()
    exit(-1)

#################################################################################################################

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", help="input sysex (.syx) file", dest="inputfile",  metavar="<input file>")
    (opts, args) = parser.parse_args()

if (opts.inputfile is None):
    print("Error: <input file> not specified\n")
    printHelpAndExit()

try:
    f = open(opts.inputfile, "rb").read()
except IOError:
    print("Error: could not open: %s\n"%(opts.inputfile))
    exit(-1)

try:
    print(yamahadx7_syx.SysEx(f).prettyPrint())
    #print(binascii.hexlify(yamahadx7_syx.SysEx(f).dump()))
    print(hexdump.hexdump(yamahadx7_syx.SysEx(f).dump()))
    exit(0)
except Exception as e:
    print(e)
    pass


try:
   print(rolandjx8p_syx.RolandJX8PSysEx(f).prettyPrint())
   exit(0)
except Exception as e:
   print(e)
   pass

print("Error: unknown sysex format: %s"%(opts.inputfile))
exit(-1)

