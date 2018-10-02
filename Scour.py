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
import hexdump
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
    parser.add_option("-o", help="output directory (default: ./out)", dest="outputdir",  metavar="<directory>")
    parser.add_option("-x", help="don't ask (just do)", action="store_true", dest="dontask",  default=False)
    (opts, args) = parser.parse_args()

if (opts.inputdir is None):
    print("Error: <directory> not specified\n")
    printHelpAndExit()

if not os.path.isdir(opts.inputdir):
    print("Error: input <directory> does not exist: %s\n"%(opts.inputdir))
    printHelpAndExit()

if (opts.outputdir is None):
    opts.outputdir = "%s/out"%(os.getcwd())

print "\nInput directory: %s"%(opts.inputdir)
print "Output directory: %s"%(opts.outputdir)

if os.path.isdir(opts.outputdir):
    print("\nWARNING: output directory exists: %s"%(opts.outputdir))
    print("... this is OK, but it is your responsibility to make sure it has not been corrupted!\n")

if (opts.dontask is False):   
    print ""
    response = raw_input("Is this correct? (y/n): ")
    if (not response.upper() == 'Y'):
        print ""
        print "Exiting!"
        exit(0)
    
print ""
print "Starting..."

patch_md5 = []

if os.path.isdir(opts.outputdir):
    # Recursively enumerate all existing .patch filenames below output directory, to
    # eliminate generating redundant patches
    fn_l = [y for x in os.walk(opts.outputdir) for y in glob(os.path.join(x[0], '*.patch'))]
    for fn in fn_l:
        #print fn
        try:
            f1 = open(fn, "rb")
            data = f1.read()
            f1.close()
            patch = yamahadx7_syx.Patch(data) 
            patch_md5.append(patch.getHash())
            

        except AssertionError as e:
            print str(e)
            print "WARNING: not a valid patch file: %s (skipping!)\n"%(fn)
            continue 

        except IOError:
            print "Error: could not open: %s\n"%(fn)
            exit(-1)

else:
    try:
        os.makedirs(opts.outputdir)
    except IOError:
        print "Error: could not create output directory: %s\n"%(opts.outputdir)
        exit(-1)

existing_patch_count = len(patch_md5)

skipped_syx_count = 0

# Recursively enumerate all .syx filenames below input directory
fn_l = [y for x in os.walk(opts.inputdir) for y in glob(os.path.join(x[0], '*.syx'))]
for fn in fn_l:
    #print fn
    try:
        f1 = open(fn, "rb")
        data = f1.read()
        f1.close()
    except IOError:
        print("Error: could not open: %s\n"%(fn))
        exit(-1)

    md5_input = hashlib.md5(data).hexdigest()

    try:
        syx = yamahadx7_syx.SysEx(data)           # Raises AssertionError
        md5_gen = hashlib.md5(syx.dump()).hexdigest()
        

        if md5_input != md5_gen:
            # The way the .syx actually is on disk, and the way we regenerate it programmatically, results in different binaries!
            # Likely culprits: checksum, .. FIXME
            if not syx.hasValidChecksum():
                print "The checksum on disk is: %s"%(binascii.hexlify(syx.raw_checksum))
                print "The calculated checksum is: %s"%((hex(syx.getChecksum())[2:]).zfill(2))
                raise AssertionError(".syx checksum error!")

        for patch in syx:
            if patch.getHash() in patch_md5:
                #print "Already have a patch that matches: %s"%(patch.get_name())
                pass
            else:
                print "Found new patch: %s"%(patch.get_name())
                patch_md5.append(patch.getHash())
                try:
                    f2 = open("%s/%s.patch"%(opts.outputdir, patch.getHash()), "wb")
                    f2.write(patch.dump())
                    f2.close()
                except IOError:
                    print("Error: could not write: %s/%s.patch\n"%(opts.outputdir, patch.getHash()))
                    exit(-1)

        

        #print "Success: %s"%(fn)

    

    except AssertionError as e:
        print str(e)
        print "WARNING: skipping: %s\n"%(fn)
        skipped_syx_count += 1

new_patch_count = len(patch_md5) - existing_patch_count
print "\nExisting patch count: %d"%(existing_patch_count)
print "New patch count: %d"%(new_patch_count)
print "Number of skipped .syx files: %d\n"%(skipped_syx_count)

exit(0)


