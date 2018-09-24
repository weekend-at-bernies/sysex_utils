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
import hexdump
import hashlib
from glob import glob
 


def process(fn):
    try:
        #print ""
        f = open(fn, "rb").read()
        md5_input = hashlib.md5(f).hexdigest()

        syx = yamahadx7_syx.SysEx(f)
        
        md5_gen = hashlib.md5(syx.dump()).hexdigest()

        if not syx.verifyChecksum():
            print "The checksum on disk is: %s"%(binascii.hexlify(syx.verify_checksum))
            print "The calculated checksum is: %s"%((hex(syx.getChecksum())[2:]).zfill(2))
            raise AssertionError("Checksum error!")

        if md5_input != md5_gen:
            raise AssertionError("MD5 error!")

        #print "Success: %s"%(fn)

    except IOError:
        print("Error: could not open: %s\n"%(fn))
        exit(-1)

    except AssertionError as e:
        print str(e)
        print "WARNING: skipping: %s\n"%(fn)

    



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
    print("Error: <directory> does not exist: %s\n"%(opts.inputdir))
    printHelpAndExit()

print ""
print "Input directory: %s"%(opts.inputdir)

if (opts.dontask is False):   
    print ""
    response = raw_input("Is this correct? (y/n): ")
    if (not response.upper() == 'Y'):
        print ""
        print "Exiting!"
        exit(0)
    
print ""
print "Starting..."

# Recursively enumerate all .syx files below input directory
fn_l = [y for x in os.walk(opts.inputdir) for y in glob(os.path.join(x[0], '*.syx'))]

for fn in fn_l:
    #print fn
    process(fn)

exit(0)






md5_input = hashlib.md5(f).hexdigest()
# Prints the MD5 sum of the input file:
#print "%s"%(hashlib.md5(f).hexdigest())

try:

    syx = yamahadx7_syx.SysEx(f)

    print(syx.prettyPrint())
    #hexdump.hexdump(syx.dump())

   # THIS WOULD WRITE A .syx TO FILE
   # f2 = open("yag.syx", "wb")
   # f2.write(syx.dump())
    #f2.close()

except Exception as e:
    print(e)
    exit(-1)

try:
    md5_gen = hashlib.md5(syx.dump()).hexdigest()
    assert(md5_input == md5_gen)
except AssertionError as e:
    print "Error: input MD5 and generated MD5 do not match"
    exit(-1)

exit(0)



try:
   print(rolandjx8p_syx.RolandJX8PSysEx(f).prettyPrint())
   exit(0)
except Exception as e:
   print(e)
   pass

print("Error: unknown sysex format: %s"%(opts.inputfile))
exit(-1)

