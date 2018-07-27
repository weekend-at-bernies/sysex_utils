import os
import binascii
import hashlib


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

