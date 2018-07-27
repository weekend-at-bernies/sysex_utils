#!/usr/bin/python

import os
import sys
import optparse
import rolandjx8p_syx
import yamahadx7_syx


def printHelpAndExit():
    parser.print_help()
    exit(-1)

#################################################################################################################

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", help="input sysex (.syx) file", dest="inputfile",  metavar="<input file>")
    (opts, args) = parser.parse_args()

if (opts.inputfile is None):
    print "Error: <input file> not specified"
    print ""
    printHelpAndExit()

try:
    print yamahadx7_syx.YamahaDX7SysEx(opts.inputfile).dump()
    exit(0)
except Exception as e:
    print(e)
    pass


try:
   print rolandjx8p_syx.RolandJX8PSysEx(opts.inputfile).dump()
   exit(0)
except Exception as e:
   print(e)
   pass

print "Error: unknown sysex format: %s"%(opts.inputfile)
exit(-1)

