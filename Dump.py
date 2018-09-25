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
import binascii
# Only use hexdump for python 2 (at the moment)
if not sys.version_info >= (3,0):
    import hexdump
import hashlib
 


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
    f = open(opts.inputfile, "rb")
    data = f.read()
    f.close()
except IOError:
    print("Error: could not open: %s\n"%(opts.inputfile))
    exit(-1)


#md5_input = hashlib.md5(f).hexdigest()
# Prints the MD5 sum of the input file:
#print "%s"%(hashlib.md5(f).hexdigest())

if len(data) == 4104:
    syx = yamahadx7_syx.SysEx(data)
    print(syx.prettyPrint())
elif len(data) == 128:
    patch = yamahadx7_syx.Patch(data)
    print(patch.prettyPrint())
else:
    print("Error: unknown file type: %s"%(opts.inputfile))

exit(0)




#syx = yamahadx7_syx.SysEx(data)
#print(syx.prettyPrint())
#try:

#    syx = yamahadx7_syx.SysEx(f)
#    print(syx.prettyPrint())
    
    #hexdump.hexdump(syx.dump())

   # THIS WOULD WRITE A .syx TO FILE
   # f2 = open("yag.syx", "wb")
   # f2.write(syx.dump())
    #f2.close()

#except Exception as e:
#    print(e)
#    exit(-1)

#try:
#    md5_gen = hashlib.md5(syx.dump()).hexdigest()
#    assert(md5_input == md5_gen)
#except AssertionError as e:
#    print("Error: input MD5 and generated MD5 do not match")
#    exit(-1)

#exit(0)



#try:
#   print(rolandjx8p_syx.RolandJX8PSysEx(f).prettyPrint())
#   exit(0)
#except Exception as e:
#   print(e)
#   pass

#print("Error: unknown sysex format: %s"%(opts.inputfile))
#exit(-1)

