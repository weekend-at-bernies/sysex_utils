#!/usr/bin/python

# REQUIREMENTS:
#
# https://bitbucket.org/techtonik/hexdump/ 
# $ pip install hexdump
#

import os
import sys
import optparse
#import yamahadx7_syx
#import binascii
#import hexdump
#import hashlib
#from SyxType import SyxType as SyxType
from EnumTypes import Synth as Synth
from EnumTypes import Bank as Bank
import PatchHunter
import Utils
import Settings
import Unbuffered
#from glob import glob
 
# DESCRIPTION HERE:
# Takes input directory, recursively looks for ALL .syx, and extracts UNIQUE .patch files to output directory
# Run it 





def doMenu():
    if hunter.bank == Bank.patch:
        optionLoop(getPatchMenu())
    elif hunter.bank == Bank.sysex:
        optionLoop(getSysexMenu())



def doHexDump():
    doDump(0)

def doPrettyDump():
    doDump(1)

def doPatchDump():
    doDump(2)

# Dump code:
#
# 0 - hex dump
# 1 - dump all info in human readable format
# 2 - dump only patch name(s)
#
def doDump(code):
    if len(hunter) == 0:
        print ("\nNothing to dump...")
    else:
        if len(hunter) == 1:
            n = 0
        else:
            while True:
                response = Utils.safe_raw_input("\nEnter number (between 1 and %d, inclusive): "%(len(hunter)))
                try:
                    n = int(response) - 1
                    if (n < 0) or (n >= len(hunter)):
                        raise RuntimeError
                    break
                except (RuntimeError, ValueError) as e:
                    print ("\nInvalid selection!")

        filename = hunter.enumerated[n][0]
  
        dump = hunter.enumerated[n][1].prettyPrint(code)
  
        print ("")
        print ("--------------------------------------------------------------------------------------------------------------------------------------")
        print ("File: %s\n"%(filename))
        print (dump)
        print ("--------------------------------------------------------------------------------------------------------------------------------------")

    doMenu()

def doSearch():
    response = Utils.safe_raw_input("\nEnter search string: ")
    hits = hunter.searchByName(response)
    print ("")
    if len(hits) > 0: 
        print ("Found hits...\n")
        for hit in hits:
            print ("%s %d: %s: %s"%(hunter.bank.name, hit[0], hit[1], hit[2]))
    else: 
        print ("No hits found...")
    doMenu()
     

def dumpBroken():
    print ("\nThe following have fields whose value could not be verified for correctness:")
    for x in hunter.getDodgy():
       # print ("%s: %s"%(x[1][0], x[0])
        print ("%d: %s: %s"%((x[0] + 1), x[1][0], [y.value for y in x[2]]))

def doExit():
    print ("\nExiting...")
    exit(0)

def doRepair():
    while True:
        outputdir = Utils.safe_raw_input("\nEnter output directory path: ")
        if len(outputdir) == 0:
            doMenu()
        if os.path.isdir(outputdir):
            print ("\nError: directory already exists!")
        else:
            try:
                os.makedirs(outputdir)
                break
            except IOError:
                print ("Error: could not create directory: %s\n"%(outputdir))
                continue

    if not outputdir.endswith("/"):
        outputdir = outputdir + "/"
  
    # Repair header, checksum + end marker (but don't do anything about patch names FIXME?)
    writecount = 0
    for x in hunter.getDodgy():      # x : [index, blob, unexpected fields list]
        blob = x[1]
        try:
            f = open("%s%s"%(outputdir, os.path.basename(blob[0])), "wb")
            print ("Writing: %s%s"%(outputdir, os.path.basename(blob[0])))
            f.write(blob[1].dump(True))
            f.close()
        except IOError:
            print("WARNING: could not write: %s%s"%(outputdir, os.path.basename(blob[0])))
            continue
        writecount += 1
    if writecount > 0:
        print ("\nSuccessfully wrote %d file(s) to: %s ..."%(writecount, outputdir))
    else:
        print ("\nDid not write any files to: %s ..."%(outputdir))

    #.dump(True)

    doMenu()


def doWriteUnique():
    alreadyExists = []
    while True:
        outputdir = Utils.safe_raw_input("\nEnter output directory path: ")
        if len(outputdir) == 0:
            doMenu()
        if os.path.isdir(outputdir):
            response = Utils.safe_raw_input("\nWARNING: directory already exists. Continue? (y/n): ")
            if (response.upper() == 'Y'):
                alreadyExists = Utils.getAllFilenamesWithExt(outputdir, Settings.patch_file_extension)
                break        
        else:
            try:
                os.makedirs(outputdir)
                break
            except IOError:
                print ("Error: could not create directory: %s\n"%(outputdir))
                continue

    if not outputdir.endswith("/"):
        outputdir = outputdir + "/"

#   PYTHON 2.x:
    writecount = 0
    for key, patch in hunter.unique_patches.iteritems():
        if "%s.%s"%(key, Settings.patch_file_extension) in alreadyExists:
            print ("WARNING: %s.%s already exists! Not writing..."%(key, Settings.patch_file_extension))
        else:
            try:
                f = open("%s%s.%s"%(outputdir, key, Settings.patch_file_extension), "wb")
                f.write(patch.dump())
                f.close()
            except IOError:
                print("WARNING: could not write: %s%s.%s"%(outputdir, key, Settings.patch_file_extension))
                continue
            writecount += 1
    if writecount > 0:
        print ("\nSuccessfully wrote %d .%s file(s) to: %s ..."%(writecount, Settings.patch_file_extension, outputdir))
    else:
        print ("\nDid not write any .%s files to: %s ..."%(Settings.patch_file_extension, outputdir))

#    PYTHON 3.x:
#    for key, value in d.items():

    doMenu()

def doGenSysex():
    while True:
        outputdir = Utils.safe_raw_input("\nEnter output directory path: ")
        if len(outputdir) == 0:
            doMenu()
        if os.path.isdir(outputdir):
            print ("\nError: directory already exists!")
        else:
            try:
                os.makedirs(outputdir)
                break
            except IOError:
                print ("Error: could not create directory: %s\n"%(outputdir))
                continue

    if not outputdir.endswith("/"):
        outputdir = outputdir + "/"

    l = hunter.genSysex()
    if len(l) > 0:
        sysex_l = l[0]
        leftover_patch_l = l[1]

        writecount = 0
        i = 0
        for sysex in sysex_l:
            try:
                f = open("%s%s%d.%s"%(outputdir, Settings.generated_sysex_name, i, Settings.sysex_file_extension), "wb")
                f.write(sysex.dump())
                f.close()
                writecount += 1
            except IOError:
                print("WARNING: could not write: %s%s.%s"%(outputdir, key, Settings.patch_file_extension))
                continue
            i += 1

        if writecount > 0:
            print ("\nSuccessfully wrote %d .%s file(s) to: %s"%(writecount, Settings.sysex_file_extension, outputdir))
        else:
            print ("\nDid not write any .%s files to: %s"%(Settings.sysex_file_extension, outputdir))

        writecount = 0
        for patch in leftover_patch_l:
            try:
                f = open("%s%s.%s"%(outputdir, patch.getHash(), Settings.patch_file_extension), "wb")
                f.write(patch.dump())
                f.close()
                writecount += 1
            except IOError:
                print("WARNING: could not write: %s%s.%s"%(outputdir, key, Settings.patch_file_extension))
                continue

        if writecount > 0:
            print ("Successfully wrote %d .%s file(s) to: %s"%(writecount, Settings.patch_file_extension, outputdir))
        else:
            print ("Did not write any .%s files to: %s"%(Settings.patch_file_extension, outputdir))

        


    doMenu()

def optionLoop(options):
    d = {}
    while True:
        i = 0
        print ("\nOPTIONS:\n")
        for option in options:
            print ("%d: %s"%((i + 1), option[0]))
            if len(d) < len(options):
                d[i + 1] = option[1]
            i += 1
        response = Utils.safe_raw_input("\nEnter your selection: ")
        try:
            d[int(response)]()
            break
        except (KeyError, ValueError) as e:
            print ("\nInvalid selection!")
    

def getCommonMenu():
    return [["Get summary", doSummary],
            ["Pretty dump", doPrettyDump],
            ["Hex dump", doHexDump],
            ["Patch name only dump", doPatchDump],           
            ["Patch search", doSearch],
            ["Dump broken (and suspect)", dumpBroken],    # "needs attention" list
            ["Repair broken", doRepair],                  # FIXES CHECKSUM AND HEADER... these are PARSEABLE. THE UNPARSEABLE ONES MIGHT BE A BIT TRICKY COZ FILESIZES ARENT RIGHT!!!
            ["Exit", doExit]] 



def getSysexMenu():
    return [["Write all unique patches to output directory", doWriteUnique]] + getCommonMenu()



def getPatchMenu():
    return [["Generate sysex", doGenSysex]] + getCommonMenu()


def doSummaryWork():
    print ("\nTarget synth: %s"%(synth.value))
    print ("Number of .%s files found: %d"%(bank.value, (len(hunter) + hunter.getFailedCount() + hunter.getInvalidCount())))  
    #print ("Bank type: %s"%(bank.name)
    print ("\nFailed to open: %d"%(hunter.getFailedCount()))
    print ("Failed to parse: %d"%(hunter.getInvalidCount()))
    print ("Successfully parsed: %d"%(len(hunter)))
    print ("\nPatch count: %d"%(hunter.patch_count))
    print ("Unique patch count: %d"%(len(hunter.unique_patches)))
# Broken count?

def doSummary():
    doSummaryWork()
    doMenu()



def printHelpAndExit():
    parser.print_help()
    exit(-1)

#################################################################################################################



if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", help="input directory", dest="inputdir",  metavar="<input directory>")                 # required
    parser.add_option("-b", help="bank type: %s"%(Utils.banks), dest="banktype",  metavar="<bank>")                # required
    parser.add_option("-s", help="synth type: %s"%(Utils.synths), dest="synthtype",  metavar="<synth>")            # required
    parser.add_option("-l", help="log file", dest="logfile",  metavar="<log file>")                                # optional
   # parser.add_option("-o", help="output directory (default: ./out)", dest="outputdir",  metavar="<directory>")
    parser.add_option("-x", help="don't ask (just do)", action="store_true", dest="dontask",  default=False)
    (opts, args) = parser.parse_args()

if (opts.logfile is not None):
    if os.path.isfile(opts.logfile):
        print("Error: <log file> already exists: %s\n"%(opts.logfile))
        printHelpAndExit()

    try:
        unbuffered = Unbuffered.Unbuffered(opts.logfile, sys.stdin, sys.stdout)
    except IOError:
        print("Error: <log file> already exists: %s\n"%(opts.logfile))
        printHelpAndExit()
    sys.stdout = unbuffered
    sys.stdin = unbuffered


if (opts.inputdir is None):
    print("Error: <input directory> not specified\n")
    printHelpAndExit()

if not os.path.isdir(opts.inputdir):
    print("Error: <input directory> does not exist: %s\n"%(opts.inputdir))
    printHelpAndExit()

try:
    bank = Bank[opts.banktype]
except KeyError:
    print("Error: invalid <bank> specified: %s\n"%(opts.banktype))
    printHelpAndExit() 

try:
    synth = Synth[opts.synthtype]
except KeyError:
    print("Error: invalid <synth> specified: %s\n"%(opts.synthtype))
    printHelpAndExit() 

#if (opts.outputdir is None):
#    opts.outputdir = "%s/out"%(os.getcwd())

print ("\nInput directory: %s"%(opts.inputdir))
print ("Synth type: %s"%(synth.value))
print ("Bank type: %s"%(bank.name))
print ("Target file extension: .%s"%(bank.value))
#print ("Output directory: %s"%(opts.outputdir)

#if os.path.isdir(opts.outputdir):
#    print("\nWARNING: output directory exists: %s"%(opts.outputdir))
#    print("... this is OK, but it is your responsibility to make sure it has not been corrupted!\n")

if (opts.dontask is False):   
    print ("")
    response = Utils.safe_raw_input("Is this correct? (y/n): ")
    if (not response.upper() == 'Y'):
        print ("")
        print ("Exiting!")
        exit(0)
    
print ("")
print ("Starting...")

#################################################################################################################

hunter = PatchHunter.PatchHunter(opts.inputdir, synth, bank)
doSummaryWork()


while True:
    doMenu()

exit(0)





















################################################################################################################# DEPREACTED:

patch_md5 = []

if os.path.isdir(opts.outputdir):
    # Recursively enumerate all existing .patch filenames below output directory, to
    # eliminate generating redundant patches
    fn_l = [y for x in os.walk(opts.outputdir) for y in glob(os.path.join(x[0], '*.%s'%(Settings.patch_file_extension)))]
    for fn in fn_l:
        #print fn
        try:
            f1 = open(fn, "rb")
            data = f1.read()
            f1.close()
            patch = yamahadx7_syx.Patch(data) 
            patch_md5.append(patch.getHash())
            

        except AssertionError as e:
            print (str(e))
            print ("WARNING: not a valid patch file: %s (skipping!)\n"%(fn))
            continue 

        except IOError:
            print ("Error: could not open: %s\n"%(fn))
            exit(-1)

else:
    try:
        os.makedirs(opts.outputdir)
    except IOError:
        print ("Error: could not create output directory: %s\n"%(opts.outputdir))
        exit(-1)

existing_patch_count = len(patch_md5)

skipped_syx_count = 0

################################################################################################################# DEPREACTED:

# IN directory, list of supported extensions, target synth
# OUT list of [ [filename, syx object], ... ]

# Recursively enumerate all .syx filenames below input directory
fn_l = [y for x in os.walk(opts.inputdir) for y in glob(os.path.join(x[0], '*.%s'%(Settings.sysex_file_extension)))]
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
                print ("The checksum on disk is: %s"%(binascii.hexlify(syx.raw_checksum)))
                print ("The calculated checksum is: %s"%((hex(syx.getChecksum())[2:]).zfill(2)))
                raise AssertionError(".syx checksum error!")

        for patch in syx:
            if patch.getHash() in patch_md5:
                #print ("Already have a patch that matches: %s"%(patch.get_name())
                pass
            else:
                print ("Found new patch: %s"%(patch.get_name()))
                patch_md5.append(patch.getHash())
                try:
                    f2 = open("%s/%s.patch"%(opts.outputdir, patch.getHash()), "wb")
                    f2.write(patch.dump())
                    f2.close()
                except IOError:
                    print("Error: could not write: %s/%s.patch\n"%(opts.outputdir, patch.getHash()))
                    exit(-1)

        

        #print ("Success: %s"%(fn)

    

    except AssertionError as e:
        print (str(e))
        print ("WARNING: skipping: %s\n"%(fn))
        skipped_syx_count += 1

new_patch_count = len(patch_md5) - existing_patch_count
print ("\nExisting patch count: %d"%(existing_patch_count))
print ("New patch count: %d"%(new_patch_count))
print ("Number of skipped .syx files: %d\n"%(skipped_syx_count))

exit(0)


