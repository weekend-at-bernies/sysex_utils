import os
import sys
import binascii
import hashlib
import Utils
import copy
from EnumTypes import Synth as Synth
from EnumTypes import VerifiableField as VerifiableField

# REFERENCES:
# ?

raw_sysex_data_len = 11589
sysex_header_len = 4
raw_patch_data_len = 181
raw_patch_name_len = 40
raw_patch_name_offset = 140
sysex_patch_count = 64





##################################################################################################################################
# Patch is 181 bytes, with structure:
# [140 bytes data] [ 40 bytes patch name ] [ 1 byte data ]
#
class Patch(object):

 
    # FIXME: ASCII bytes i think are between 0 and 127 (0x7F). Beyond this then you start getting UnicodeDecodeError exceptions
    # thrown ??? 
    def __str__(self):
        return self.get_name()
  

    # Hashes all data except the name of the patch
    # Can't we just call m.update(self.getComparableData()) ???
    def getHash(self):
        m = hashlib.md5()
        m.update(self.data[0:raw_patch_name_offset])
        m.update(self.data[raw_patch_data_len - 1])
        return m.hexdigest()


    # Can pass a patch individually
    def __init__(self, data, index=-1):
        assert(len(data) == raw_patch_data_len)
        self.index = index
        self.data = data


 

    
    def getComparableData(self):
        data = bytearray()
        data.extend(bytearray(self.data[0:raw_patch_name_offset]))
        data.extend(bytearray(self.data[raw_patch_data_len - 1]))  
        return bytes(data)

    # Can't we just compare hash, a la getHash() ?
    def __eq__(self, patch):
        return (self.getComparableData() == patch.getComparableData())

    


    def prettyPrint(self, n=0):
        s = ""

        if (n == 0) or (n == 2):
            s1 = "%s"%(str(self))
            if self.index >= 0:
                #if self.index == 0:
                #    s += "" #"\n"
                s += "%d: %s"%((self.index + 1), s1)
            else:
                s += s1  #"\n" + s1

            if n == 0:
                s += "\n  Patch Data (%d):\n"%(len(self.data))
                s += "    " + Utils.safe_hexdump(self.data)
            s += "\n"
           # elif n == 2:
           #     s += "\n"

        elif n == 1:
            s += "Patch (voice) name: %s\n"%(self.get_name())
            s += "Patch (voice) number: %d\n"%(self.index + 1)

        return s
    




    def getRawName(self):
        return self.data[raw_patch_name_offset:(raw_patch_name_offset + raw_patch_name_len)]


    # Returns true if the 'name' region of the data (10 bytes) is UTF-8 decodable (?)
    def isNameUTF8(self):
        try:
            binascii.unhexlify(Utils.safe_binascii_hexlify(self.getRawName())).decode()
            return True
        except UnicodeDecodeError:
            return False

    def get_name(self):
        # Python 3 only:
        if sys.version_info >= (3,0):
            return binascii.unhexlify(Utils.safe_binascii_hexlify(str(self.getRawName()).encode().strip())).decode('unicode-escape')[2:-1]
#           return binascii.unhexlify(str(self.data[16:]))
        # Python 2 only:
        else:          
            return binascii.unhexlify(str(self.getRawName()))
            # return binascii.hexlify(self.data[16:])       <--- returns the hex as a string



    def hasASCIIname(self):
        #return all(ord(c) < 128 for c in str(self.data[16:]))
        if all(Utils.safe_ord(c) < 128 for c in str(self.getRawName())):       #  < 7f
            return True
        else:
            #print binascii.hexlify(self.data[16:])
            return False


   
    # DUMP AS BINARY
    def dump(self):
        data = bytearray()
        data.extend(bytearray(self.data))
        return bytes(data)


##################################################################################################################################


# .syx is a bank of 64 patches 
# It is 11589 bytes length, with structure:
# [4 byte header] [ 64 * 181 byte patches ]  [1 byte endmarker 'F7']
class SysEx(object):


    def get(self):
        return self


    def getType(self):
        return Synth.yamaha_tx802


    # IN: .syx binary or list of 64 patches
    def __init__(self, data):  

        self.patches = []

        
        if ((type(data) is str) or (type(data) is bytes)):
 
            # Python 2 will get 'str'
            # Python 3 will get 'bytes'
            
            assert(len(data) == raw_sysex_data_len)

         
            i2 = sysex_header_len
            for i1 in range(sysex_patch_count):
                self.patches.append(Patch(data[i2:(i2 + raw_patch_data_len)], i1))
                i2 += raw_patch_data_len

        elif type(data) is list:

            assert(len(data) == sysex_patch_count)
            #self.patches = copy.copy(data)   #copy.deepcopy(data)
            
            self.patches = list(data)



    def __len__(self):
        return len(self.patches)
 
    def __iter__(self):
        return iter(self.patches)


    def prettyPrint(self, n=0):
        s = ""

        if n == 0:
            for patch in self:
                s += patch.prettyPrint(0) + "\n"
            s += "\n"
        else:
            for patch in self:
                s += patch.prettyPrint(n)
        return s

    # Returns a list of the patches that have a given string in the name
    def getPatchesByName(self, name):
        l = []
        for patch in self:
            if name.lower() in str(patch).lower():
                l.append(patch)
        return l



    # DUMP AS BINARY
    def dump(self, corrected=False):
        data = bytearray()
        data.extend(bytearray(self.data[0:sysex_header_len]))
        for patch in self:
            data.extend(bytearray(patch.dump()))
        data.extend(bytearray(self.data[raw_sysex_data_len]))
        return bytes(data)



        

##################################################################################################################################

