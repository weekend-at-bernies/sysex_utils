import sys
import binascii
import Settings
import hexdump
import os
from glob import glob
from EnumTypes import FileType as FileType
from EnumTypes import Bank as Bank
from EnumTypes import Synth as Synth

# REQUIREMENTS:
#
# https://bitbucket.org/techtonik/hexdump/ 
#
# Python 2.x:
# $ pip install hexdump
#
# Python 3+:
# $ pip3 install hexdump
# 


# Supports Python 2.x and 3+
def safe_raw_input(s):
    if sys.version_info >= (3,0):
        return input(s)
    else:
        return raw_input(s)


# Supports Python 2.x and 3+
def safe_binascii_hexlify(n):     
    if sys.version_info >= (3,0):
        if type(n) is bytes:
            return binascii.hexlify(bytes(n))
        elif type(n) is int:
            return binascii.hexlify(bytes([n]))

       #  FIXME: raise RuntimeError
    else:
        return binascii.hexlify(n)

# Supports Python 2.x and 3+
def safe_hexdump(b):
    #return hexdump.hexdump(b)
    if sys.version_info >= (3,0):

        if type(b) is bytes:
            return hexdump.dump(bytes(b))    
        elif type(b) is int:
            return hexdump.dump(bytes([b]))       

        # FIXME: raise RuntimeError

    else:
        return hexdump.dump(b)

# Returns a list of ALL filenames with a specified file extension ('target_ext') that exist inside a specified directory ('target_dir') : this is NON-RECURSIVE.
# FIXME ASSERT: only lists filenames, not the complete path. So if target_dir is /tmp and a file is /tmp/foo.txt, it will only list "foo.txt" 
# FIXME ASSERT: It will NOT look below subdirectories.
def getAllFilenamesWithExt(target_dir, target_ext):
#    files = filter(os.path.isfile, os.listdir(target_dir)) 
#    files = list(filter(lambda x: x.endswith(".%s"%(target_ext)), os.listdir(target_dir)))
#    print files
    return list(filter(lambda x: x.endswith(".%s"%(target_ext)), os.listdir(target_dir)))
# If you wanted to do this recursively, you'd do:
# list(filter(lambda x: x < 0, number_list))
    #return [y for x in os.walk(target_dir) for y in glob(os.path.join(x[0], '*.%s'%(target_ext)))]
    

def safe_ord(b):
    if sys.version_info >= (3,0):

        if type(b) is bytes:
            # gets here header check
            #print("bytes %s"%(safe_binascii_hexlify(b)))       

            # SEEMS TO WORK
            return bytes(b)

        elif type(b) is int:
            #print("int: %d"%(b))
            # gets here 
            #print("YO: " + binascii.unhexlify(bytes(b)))
            
           # return ord(binascii.unhexlify(b))
            return ord(bytes([b]))       

        # FIXME: raise RuntimeError

    else:
        return ord(b)


#exts_dict =  {Bank.sysex:Settings.sysex_file_extension, Bank.patch:Settings.patch_file_extension}

filetypes = list(f.name for f in FileType)  
banks = list(b.name for b in Bank)  
synths = list(s.name for s in Synth)


