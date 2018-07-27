import os
import binascii
import hashlib

LFOWaves = {0: "Triangle", 1: "Sawtooth Down", 2: "Sawtooth Up", 3: "Square", 4: "Sine", 5: "Sample and Hold"}
Notes = {0 : "C", 1 : "C#", 2 : "D", 3 : "D#", 4 : "E", 5 : "F", 6 : "F#", 7 : "G", 8 : "G#", 9 : "A", 10 : "A#", 11 : "B"}
OscillatorMode = {0 : "Frequency (Ratio)", 1 : "Fixed Frequency (Hz)"}

class YamahaDX7Patch(object):

   ##################################################################################################################################
   class Operator():
       def __init__(self, data, index):
           self.index = index
           self.data = data

           self.EG_R1 = int(binascii.hexlify(data[0]), 16)
           self.EG_R2= int(binascii.hexlify(data[1]), 16)
           self.EG_R3= int(binascii.hexlify(data[2]), 16)
           self.EG_R4= int(binascii.hexlify(data[3]), 16)
           self.EG_L1= int(binascii.hexlify(data[4]), 16)
           self.EG_L2= int(binascii.hexlify(data[5]), 16)
           self.EG_L3= int(binascii.hexlify(data[6]), 16)
           self.EG_L4= int(binascii.hexlify(data[7]), 16)

           # DEL BELOW
           self.levelScalingBreakPoint = data[8]
           self.scaleLeftDepth = data[9]
           self.scaleRightDepth = data[10]

           self.scaleCurve = data[11] 

           self.rateScaleDetune = data[12] 

           self.sensitivity = data[13]
           self.outputLevel= data[14]

           self.oscillatorModeFreq = data[15]
           self.frequencyFine = data[16]
           # DEL ABOVE

           self.AMsens = int(binascii.hexlify(data[13]), 16) & 0x3
           self.oscillmode = int(binascii.hexlify(data[15]), 16) & 0x1
           self.frequencyCoarse = (int(binascii.hexlify(data[15]), 16) & 0x3E) >> 1 
           self.frequencyFine = int(binascii.hexlify(data[16]), 16)
           self.detune = (int(binascii.hexlify(data[12]), 16) & 0x78) >> 3 

           # FIX ME, to do:
           # Verify self.toByteArray() works:
           # testdata = self.toByteArray()
           # testdata == data ??


       def dump(self):
           s = ""
           s += "  Operator number: %d\n"%(self.index + 1)
           s += "    AM Sensitivity: %d\n"%(self.AMsens)
           s += "    Oscillator Mode: %s\n"%(OscillatorMode.get(self.oscillmode, "Unknown oscillator mode type"))
           s += "    Frequency: %.2f\n"%(self.getFrequency())
           s += "    Detune: %d\n"%(self.detune - 7)
           s += "    Envelope Generator\n"
           s += "      Rate 1: %d\n"%(self.EG_R1)
           s += "      Rate 2: %d\n"%(self.EG_R2)
           s += "      Rate 3: %d\n"%(self.EG_R3)
           s += "      Rate 4: %d\n"%(self.EG_R4)
           s += "      Level 1: %d\n"%(self.EG_L1)
           s += "      Level 2: %d\n"%(self.EG_L2)
           s += "      Level 3: %d\n"%(self.EG_L3)
           s += "      Level 4: %d\n"%(self.EG_L4)
           s += "    Keyboard Level Scaling\n"
           return s


       def getFrequency(self):
           if self.oscillmode == 0:
               coarse = float(self.frequencyCoarse)
               if (coarse == 0):
                   coarse = 0.5
               freq = coarse + (float(self.frequencyFine) * coarse / 100)
           elif self.oscillmode == 1:
               power = float(self.frequencyCoarse % 4) + (float(self.frequencyFine) / 100)
               freq = pow(10, power) 
           else:
               return -1
           return freq



          # // If ratio mode
          #  if (op.oscillatorMode == 0)
          #  {
          #      double coarse = op.frequencyCoarse;
          #      if (coarse == 0)
          #          coarse = .5;

#                const double freq = coarse + 
 #                   ((double)op.frequencyFine * coarse / 100);
  #              
   #             printf("  Frequency: %g\n", freq);
    #        }
     #       else  // fixed mode
      #      {
       #         const double power = (double)(op.frequencyCoarse % 4) +
        #                             (double)op.frequencyFine / 100;
         #       const double f = pow(10, power);
          #      printf("  Frequency: %gHz\n", f);
           # }

       
       def toByteArray(self):
           return
           # FIX ME, to do:
           # data = byte_array[0:16] , or however many bytes
           # data[0] = to_unsigned_hex(self.EG_R1)
           # ... etc
           # return data
           # 
           
  

   ##################################################################################################################################


   def __str__(self):
        return self.name

   
   def __iter__(self):
        #return iter(list(reversed(self.operators)))
        return iter(self.operators)

   # Hashes all data except the name of the patch
   def getHash(self):
       m = hashlib.sha256()
       m.update(self.data[:118])
       return m.hexdigest()
     
   def process(self, data):
       n = 0
       self.operators = []
       for i in range(6):
          # self.operators.append(self.Operator(data[n:(n + 18)], i))
           # For some crazy reason, operators are set out in reverse?? ie. operator 1 is at the back of the binary data list
           self.operators.insert(0, self.Operator(data[n:(n + 18)], (5 - i))) 
           n += 17

       self.pitchEGR1 = int(binascii.hexlify(data[102]), 16) 
       self.pitchEGR2 = int(binascii.hexlify(data[103]), 16) 
       self.pitchEGR3 = int(binascii.hexlify(data[104]), 16) 
       self.pitchEGR4 = int(binascii.hexlify(data[105]), 16) 
       self.pitchEGL1 = int(binascii.hexlify(data[106]), 16) 
       self.pitchEGL2 = int(binascii.hexlify(data[107]), 16) 
       self.pitchEGL3 = int(binascii.hexlify(data[108]), 16) 
       self.pitchEGL4 = int(binascii.hexlify(data[109]), 16)

       self.algorithm = (int(binascii.hexlify(data[110]), 16) & 0x1F) + 1
       self.feedback =  int(binascii.hexlify(data[111]), 16) & 0x7

       self.lfowave = (int(binascii.hexlify(data[116]), 16) & 0xE) >> 1
       self.lfospeed = int(binascii.hexlify(data[112]), 16) 
       self.lfodelay = int(binascii.hexlify(data[113]), 16) 
       self.lfopitchmoddepth = int(binascii.hexlify(data[114]), 16) 
       self.lfoamdepth = int(binascii.hexlify(data[115]), 16) 
       self.lfosync = bool(int(binascii.hexlify(data[116]), 16) & 0x1)
       self.lfopitchmodsens = (int(binascii.hexlify(data[116]), 16) & 0xF0) >> 4   
   
       self.osckeysens = bool((int(binascii.hexlify(data[111]), 16) & 0x8) >> 3)
       self.transpose = int(binascii.hexlify(data[117]), 16)

       self.name = binascii.unhexlify(binascii.hexlify(data[118:]))

       #print self.name
#binascii.unhexlify("666f6f")
#print binascii.b2a_uu(data[118:])

   def dump(self):
       s = "\n"
       s += "Patch (voice) name: %s\n"%(self.name)
       s += "Patch (voice) number: %d\n"%(self.index + 1)
       s += "Algorithm: %d\n"%(self.algorithm)
       s += "Feedback: %d\n"%(self.feedback)
       s += "LFO\n"
       s += "  Wave: %s\n"%(LFOWaves.get(self.lfowave, "Unknown LFO wave type"))
       s += "  Speed: %d\n"%(self.lfospeed)
       s += "  Delay: %d\n"%(self.lfodelay)
       s += "  Pitch Mod Depth: %d\n"%(self.lfopitchmoddepth)
       s += "  AM Depth: %d\n"%(self.lfoamdepth)
       s += "  Sync: %s\n"%(self.lfosync)
       s += "  Pitch Modulation Sensitivity: %d\n"%(self.lfopitchmodsens)
       s += "Oscillator Key Sync: %s\n"%(self.osckeysens)
       s += "Pitch Envelope Generator\n"
       s += "  Rate 1: %d\n"%(self.pitchEGR1)
       s += "  Rate 2: %d\n"%(self.pitchEGR2)
       s += "  Rate 3: %d\n"%(self.pitchEGR3)
       s += "  Rate 4: %d\n"%(self.pitchEGR4)
       s += "  Level 1: %d\n"%(self.pitchEGL1)
       s += "  Level 2: %d\n"%(self.pitchEGL2)
       s += "  Level 3: %d\n"%(self.pitchEGL3)
       s += "  Level 4: %d\n"%(self.pitchEGL4)
       s += "Transpose: %s\n"%(self.getTransposeStr())
       for operator in self:
           s += "\n"
           s += operator.dump()

       return s

   def hasValidTranspose(self):
       if (self.transpose >= 0) and (self.transpose <= 48):
           return True
       return False

   def getTransposeStr(self):
       s = "out of range"
       if self.hasValidTranspose():
           return "%s%d"%(Notes.get((self.transpose % 12), s), ((self.transpose / 12) + 1))
       return s
           

   # Potentially pass these as separate files
   def __init__(self, data, hostfile, index):
       self.index = index
       if data is None:
           # open hostfile and try to parse that, setting self.data
           self.index = -1
           pass
       else:
           # input1 is data
           self.hostfile = hostfile  # doesn't necessarily have to be a valid .syx file
           self.data = data
           self.process(data)
           

##################################################################################################################################


# Yamaha DX7 .syx file containing 32 patches
class YamahaDX7SysEx(object):

    def isValidHeader(self, data):
      # print binascii.hexlify(data[0])
       if data[0] == b'\xF0' and \
          data[1] == b'\x43' and \
          data[2] == b'\x00' and \
          data[3] == b'\x09' and \
          data[4] == b'\x20' and \
          data[5] == b'\x00':
          return True
       return False



    # IN: path to the .syx file
    def __init__(self, filepath):
        self.filepath = filepath
        self.patches = []

        with open(filepath, "rb") as f:
            self.data = f.read()
         
        self.hasValidHeader = self.isValidHeader(self.data[0:6])
  
        if self.hasValidHeader:
          
            n = 6
            for i in range(32):
                self.patches.append(YamahaDX7Patch(self.data[n:(n + 129)], filepath, i))
                n += 128
 
        else:
            raise TypeError("Not a Yamaha DX7 compatible .syx file")

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

    #def getPatchesByApproxName(self, name):
    def findPatchesByName(self, name):
        l = []
        for patch in self:
            if name.lower() in patch.name.lower():
                l.append(patch)
        return l

