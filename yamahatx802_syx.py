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

raw_sysex_data_len = 4960
raw_patch_data_len = 155
raw_patch_name_len = 10
raw_patch_name_offset = 145
sysex_patch_count = 32

raw_operator_data_len = 21
patch_operator_count = 6

##################################################################################################################################

class Operator(object):

    #        The structure of a single valid Yamaha TX802 operator is like this:
    #
    #        [Operator]             <--- 21 bytes
    # 
    def __init__(self, data, index):
        assert(len(data) == raw_operator_data_len)
        self.index = index
        self.data = data

    # DUMP AS BINARY
    def dump(self):
        data = bytearray()
        data.extend(bytearray(self.data))
        return bytes(data)


    def prettyPrint(self, n=0):
        s = ""
        if n == 0:
            s += "\n  Operator (%d):\n"%(len(self.data))
            s += "    " + Utils.safe_hexdump(self.data)
        else:
            pass
        return s

##################################################################################################################################
# Patch is 155 bytes length
#
# 10 bytes is the patch name
# That leaves 145 bytes of patch data
#
# Compare this to a DX7 patch (128 bytes inc. 10 byte patch name):

    #        The structure of a single valid Yamaha DX7 patch is like this:
    #
    #        [Operator 1] [Operator 2] .... [Operator 6] [26 byte patch data]
    #
    #        Where:
    #        [Operator]             <--- 17 bytes
    #
    #        So its total size is calculated like this:
    #
    #        (6 * 17) + 26 = 128 bytes 
    #
    #        And the structure of [26 byte patch data] is like this:
    #        
    #        [16 bytes data] [10 bytes patch name]

#
# So the TX802 has 145 - 118 = 27 extra bytes

# Apparently TX802 loads DX7 patches ????


class Patch(object):

    
   
    # FIXME: ASCII bytes i think are between 0 and 127 (0x7F). Beyond this then you start getting UnicodeDecodeError exceptions
    # thrown ??? 
    def __str__(self):
        return self.get_name()
  
    def __iter__(self):
        #return iter(list(reversed(self.operators)))
        return iter(self.operators)


    # Hashes all data except the name of the patch
    def getHash(self):
        #m = hashlib.md5()
        #m.update(self.data[:118])
        #return m.hexdigest()
        #return hashlib.md5(self.data[0:144]).hexdigest()
        self.rel_patch_name_offset = raw_patch_name_offset - (raw_operator_data_len * patch_operator_count)
        return hashlib.md5(self.data[0:self.rel_patch_name_offset]).hexdigest()         # NEED TO VERIFY


    # Can pass a patch individually
    def __init__(self, data, index=-1):
        #assert(len(data) == 155)
        assert(len(data) == raw_patch_data_len)
        self.index = index
       # self.data = data[0:]
        self.data = data[(raw_operator_data_len * patch_operator_count):]
       # assert(len(self.data) == 26)

        i2 = 0
        self.operators = []
        # In the binary structure, operators are laid out in reverse order (so the first one is operator 6, etc.)
        # FIXME: does the order of operators affect equality? Suppose i have 2 operators: A, B. Does patch 1 (A,B) == patch 2 (B,A) ???
        for i1 in range(patch_operator_count):
            self.operators.append(Operator(data[i2:(i2 + raw_operator_data_len)], ((patch_operator_count - 1) - i1)))
            i2 += patch_operator_count
       
 


    def getComparableData(self):
        data = bytearray()
        #data.extend(bytearray(self.data[0:144]))
        data.extend(bytearray(self.data[0:self.rel_patch_name_offset]))         # NEED TO VERIFY
        return bytes(data)


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
                for operator in self:               
                    s += operator.prettyPrint(n)
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
        return self.data[self.rel_patch_name_offset:raw_patch_data_len]


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
            return str(self.getRawName())
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


# .syx is a bank of 32 patches (this is NOT the performance bank)
# It is 4960 bytes length (4960 bytes / 32 patches = 155 bytes per patch)
class SysEx(object):

    def getType(self):
        return Synth.yamaha_tx802


    # IN: .syx binary or list of 32 patches
    def __init__(self, data):  

        self.patches = []

        
        if ((type(data) is str) or (type(data) is bytes)):
 
            # Python 2 will get 'str'
            # Python 3 will get 'bytes'
            
            assert(len(data) == raw_sysex_data_len)

         
            i2 = 0
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
        for patch in self:
            data.extend(bytearray(patch.dump()))
        return bytes(data)



        

##################################################################################################################################

