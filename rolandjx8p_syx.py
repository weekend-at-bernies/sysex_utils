import os
import binascii
import hashlib

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

