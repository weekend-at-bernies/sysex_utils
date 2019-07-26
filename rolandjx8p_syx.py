import os
import sys
import binascii
import hashlib
import Utils
import copy
from EnumTypes import Synth as Synth
from EnumTypes import VerifiableField as VerifiableField

# REFERENCES:

# http://llamamusic.com/super-jx/mks70SysEx_I.html
# This reference explains the header:
# F0 : Start of System Exclusive message 
# 41 : Synthesizer manufacturer (Roland == 41)
# 35 : IPR (individual parameter) ???   When the JX-8P transmits a sysex, this will be 36
# 00 : MIDI channel (00 == channel 1, 01 == channel 2, etc.)
# 21 : Data was sent from ????
# 20 : After the header, the information contains ????   When the JX-8P transmits a sysex, this will be 30
# 01 : Group number

# https://www.gearslutz.com/board/electronic-music-instruments-and-electronic-music-production/789017-jx8p-novation-remote-zero-sl-mk-i-sysex-help.html
# There is some (conflicting) info here
# F0 :
# 41 :
# 35 : Operation code? Parameter?
# 00 :
# 21 : Format type?
# 20 : Level # ??? In this case 1 ??
# 01

# http://www.wolzow.com/analog/jx-10-bulkdump.htm
# This reference clarifies Group # and Level #:
# Level # = 20 (Tone), 30 (Patch)
# Group # = 01 (Tone A), 02 (Tone B)

# http://www.synthzone.com/mschreier/html/files/jx-8p.pdf
# Right at the back of the official manual is a section called "JX-8P MIDI IMPLEMENTATION"

# http://www.wolzow.com/analog/jx-10-bulkdump.htm
# https://dialogaudio.com/modulationprocessor/sysex_info.php
# http://forum.vintagesynth.com/viewtopic.php?f=5&t=68005
# https://translate.google.com.au/translate?hl=en&sl=fr&u=https://fr.audiofanzine.com/synthe-analogique/roland/JUNO-106/forums/t.482378,impossible-de-charger-certains-sysex-achetes-sur-le-web-dans-mon-juno-106.html&prev=search


# DEPRECATED (don't use):
class RolandJX8PPatch(object):

   
   def __str__(self):
        return self.name

   
   #def __iter__(self):
        #return iter(list(reversed(self.operators)))
   #     return iter(self.operators)

   # Hashes all data except the name of the patch
   #def getHash(self):
   #    m = hashlib.sha256()
   #    m.update(self.data[:118])
   #    return m.hexdigest()
     
   def process(self, data):

       self.name = binascii.unhexlify(binascii.hexlify(data[7:17]))


   def dump(self):
       s = "\n"
       s += "Patch (voice) name: %s\n"%(self.name)
       s += "Patch (voice) number: %d\n"%(self.index + 1)
       return s


           

   # Potentially pass these as separate files
   def __init__(self, data, hostfile, index):
       self.index = index
       if data is None:
           # open hostfile and try to parse that, setting self.data ??????
           self.index = -1
           pass
       else:
           # input1 is data
           self.hostfile = hostfile  # doesn't necessarily have to be a valid .syx file ??????
           self.data = data
           self.process(data)
           

##################################################################################################################################


# DEPRECATED (don't use):
#
# Roland JX8P .syx file containing variable number patches ???
class RolandJX8PSysEx(object):

    # REFERENCE: http://llamamusic.com/super-jx/mks70SysEx_I.html
    def isValidHeader(self, data):
      # print binascii.hexlify(data[0])
       if data[0] == b'\xF0' and \
          data[1] == b'\x41' and \
          data[2] == b'\x35' and \
          data[3] == b'\x00' and \
          data[4] == b'\x21' and \
          data[5] == b'\x20' and \
          data[6] == b'\x01':
          return True
       return False


       # Start of System Exclusive message
       # Synth manufacturer (41 == Roland)
       # Operation Code
       # Unit Number
       # Format Type
       # Level 2 Patch
       # Group Number

    # IN: path to the .syx file
    def __init__(self, filepath):
        self.filepath = filepath
        self.patches = []

        with open(filepath, "rb") as f:
            self.data = f.read()
         
        self.hasValidHeader = self.isValidHeader(self.data[0:7])
  
        if self.hasValidHeader:
            i = 0
            n = 0
            while n < os.path.getsize(filepath):
                self.patches.append(RolandJX8PPatch(self.data[n:(n + 78)], filepath, i))
                i += 1
                n += 78
 
        else:
            raise TypeError("Not a Roland JX-8P compatible .syx file")

    def __str__(self):
        return self.filepath

    def __iter__(self):
        return iter(self.patches)

    def dump(self):
        s = ""
        s += "Filename: %s\n"%(self.filepath)
        for patch in self:
            s += patch.dump()
        return s

    #def findPatchesByName(self, name):
    #    l = []
    #    for patch in self:
    #        if name.lower() in patch.name.lower():
    #            l.append(patch)
    #    return l





##################################################################################################################################
# A patch is 78 bytes length
# It is structured like this:
#
# [ 7 bytes data ] [ 11 bytes patch name ] [ 52 bytes data ]         <-- we've gone with 11 bytes patch name even tho doco says 18 bytes. In the example .syx, the patch names are definitely < 18 bytes


class Patch(object):
   
    # FIXME: ASCII bytes i think are between 0 and 127 (0x7F). Beyond this then you start getting UnicodeDecodeError exceptions
    # thrown ??? 
    def __str__(self):
        return self.get_name()
  
   # def __iter__(self):
   #     #return iter(list(reversed(self.operators)))
   #     return iter(self.operators)

    # Hashes all data except the name of the patch
    def getHash(self):
        #m = hashlib.md5()
        #m.update(self.data[:118])
        #return m.hexdigest()
        data = bytearray()
        data.extend(bytearray(self.data[0:7]))
        # skip over patch name
        data.extend(bytearray(self.data[18:]))
        return hashlib.md5(data).hexdigest()


    # Can pass a patch individually
    def __init__(self, data, index=-1):
        assert(len(data) == 78)
        self.index = index
        self.data = data[0:]
       # assert(len(self.data) == 26)
       
 


    def getComparableData(self):
        data = bytearray()
        data.extend(bytearray(self.data[0:7]))
        # skip over patch name
        data.extend(bytearray(self.data[18:]))
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
                s += "\n  Patch Data:\n"
                s += "    " + Utils.safe_hexdump(self.data)
            s += "\n"
           # elif n == 2:
           #     s += "\n"

        elif n == 1:
            s += "Patch (voice) name: %s\n"%(self.get_name())
            s += "Patch (voice) number: %d\n"%(self.index + 1)

        return s
    


    # Returns true if the 'name' region of the data (10 bytes) is UTF-8 decodable (?)
    def isNameUTF8(self):
        try:
            binascii.unhexlify(Utils.safe_binascii_hexlify(self.data[7:18])).decode()
            return True
        except UnicodeDecodeError:
            return False

    def get_name(self):
        # Python 3 only:
        if sys.version_info >= (3,0):
            return binascii.unhexlify(Utils.safe_binascii_hexlify(str(self.data[7:18]).encode().strip())).decode('unicode-escape')[2:-1]
#           return binascii.unhexlify(str(self.data[16:]))
        # Python 2 only:
        else:          
            return str(self.data[7:18])
            # return binascii.hexlify(self.data[16:])       <--- returns the hex as a string



    def hasASCIIname(self):
        #return all(ord(c) < 128 for c in str(self.data[16:]))
        if all(Utils.safe_ord(c) < 128 for c in str(self.data[7:25])):       #  < 7f
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


# .syx is a bank of 32 patches 
# It is 2496 bytes length (2496 bytes / 32 patches = 78 bytes per patch)
class SysEx(object):

    def getType(self):
        return Synth.roland_jx8p


    # IN: .syx binary or list of 32 patches
    def __init__(self, data):  

        self.patches = []

        
        if ((type(data) is str) or (type(data) is bytes)):
 
            # Python 2 will get 'str'
            # Python 3 will get 'bytes'
            
            assert(len(data) == 2496)

            
         
            i2 = 0
            for i1 in range(32):
                self.patches.append(Patch(data[i2:(i2 + 78)], i1))
                i2 += 78

        elif type(data) is list:

            assert(len(data) == 32)
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

