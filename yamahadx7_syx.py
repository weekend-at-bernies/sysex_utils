import os
import sys
import binascii
import hashlib
import Utils
import copy
from EnumTypes import Synth as Synth
from EnumTypes import VerifiableField as VerifiableField

LFOWaves = {0: "Triangle", 1: "Sawtooth Down", 2: "Sawtooth Up", 3: "Square", 4: "Sine", 5: "Sample and Hold"}
Notes = {0 : "C", 1 : "C#", 2 : "D", 3 : "D#", 4 : "E", 5 : "F", 6 : "F#", 7 : "G", 8 : "G#", 9 : "A", 10 : "A#", 11 : "B"}
OscillatorMode = {0 : "Frequency (Ratio)", 1 : "Fixed Frequency (Hz)"}

# https://www.devdungeon.com/content/working-binary-data-python


##################################################################################################################################

class Operator(object):

    #        The structure of a single valid Yamaha DX7 operator is like this:
    #
    #        [Operator]             <--- 17 bytes
    # 
    def __init__(self, data, index):
        assert(len(data) == 17)
        self.index = index
        self.data = data


    def hasFloatingEndMarker(self):
        #return all(ord(c) < 128 for c in str(self.data[16:]))
       # for c in str(self.data[:]):
            #print ord(c)
        #    if c == b'\xE2':
         #       print "POO3"
        if sys.version_info >= (3,0):
            #   print(str(type(self.raw_endmarker)) + " and " + str(type(self.getValidEndmarker())))
          #  print(str(type(self.data[16:])))
            #for b in self.data[:]:
            #    if b == 247:
            #        print("AVOOZL")


            if all(b != 247 for b in self.data[:]):       #  != F7                
                return False
            else:
                #print binascii.hexlify(self.data[16:])
                return True
        else:
            if all(Utils.safe_ord(c) != 247 for c in str(self.data[:])):       #  != F7
                return False
            else:
                #print binascii.hexlify(self.data[16:])
                return True




    def get_EG_R1(self):
        return int(Utils.safe_binascii_hexlify(self.data[0]), 16) 
    def get_EG_R2(self):
        return int(Utils.safe_binascii_hexlify(self.data[1]), 16) 
    def get_EG_R3(self):
        return int(Utils.safe_binascii_hexlify(self.data[2]), 16) 
    def get_EG_R4(self):
        return int(Utils.safe_binascii_hexlify(self.data[3]), 16) 
    def get_EG_L1(self):
        return int(Utils.safe_binascii_hexlify(self.data[4]), 16) 
    def get_EG_L2(self):
        return int(Utils.safe_binascii_hexlify(self.data[5]), 16) 
    def get_EG_L3(self):
        return int(Utils.safe_binascii_hexlify(self.data[6]), 16) 
    def get_EG_L4(self):
        return int(Utils.safe_binascii_hexlify(self.data[7]), 16) 

#### FIXME BELOW   WHAT ARE THEY, WHERE DID YOU GET THIS INFO
    def get_levelScalingBreakPoint(self):
        return int(Utils.safe_binascii_hexlify(self.data[8]), 16) 
    def get_scaleLeftDepth(self):
        return int(Utils.safe_binascii_hexlify(self.data[9]), 16) 
    def get_scaleRightDepth(self):
        return int(Utils.safe_binascii_hexlify(self.data[10]), 16) 
    def get_scaleCurve(self):
        return int(Utils.safe_binascii_hexlify(self.data[11]), 16) 
    def get_rateScaleDetune(self):
        return int(Utils.safe_binascii_hexlify(self.data[12]), 16) 
    def get_sensitivity(self):
        return int(Utils.safe_binascii_hexlify(self.data[13]), 16) 
    def get_outputLevel(self):
        return int(Utils.safe_binascii_hexlify(self.data[14]), 16) 
    def get_oscillatorModeFreq(self):
        return int(Utils.safe_binascii_hexlify(self.data[15]), 16) 
    def get_frequencyFine(self):
        return int(Utils.safe_binascii_hexlify(self.data[16]), 16) 
#### FIXME ABOVE

    def get_AMsens(self):
        return int(Utils.safe_binascii_hexlify(self.data[13]), 16) & 0x3
    def get_oscillmode(self):
        return int(Utils.safe_binascii_hexlify(self.data[15]), 16) & 0x1
    def get_frequencyCoarse(self):
        return (int(Utils.safe_binascii_hexlify(self.data[15]), 16) & 0x3E) >> 1 
    def get_frequencyFine(self):
        return int(Utils.safe_binascii_hexlify(self.data[16]), 16)
    def get_detune(self):
        return (int(Utils.safe_binascii_hexlify(self.data[12]), 16) & 0x78) >> 3 



    def prettyPrint(self, n=0):
        s = ""
        if n == 0:
            s += "\n  Operator:\n"
            s += "    " + Utils.safe_hexdump(self.data)
        else:
            s += "  Operator number: %d\n"%(self.index + 1)
            s += "    AM Sensitivity: %d\n"%(self.get_AMsens())
            s += "    Oscillator Mode: %s\n"%(OscillatorMode.get(self.get_oscillmode(), "Unknown oscillator mode type"))
            s += "    Frequency: %.2f\n"%(self.getFrequency())
            s += "    Detune: %d\n"%(self.get_detune() - 7)
            s += "    Envelope Generator\n"
            s += "      Rate 1: %d\n"%(self.get_EG_R1())
            s += "      Rate 2: %d\n"%(self.get_EG_R2())
            s += "      Rate 3: %d\n"%(self.get_EG_R3())
            s += "      Rate 4: %d\n"%(self.get_EG_R4())
            s += "      Level 1: %d\n"%(self.get_EG_L1())
            s += "      Level 2: %d\n"%(self.get_EG_L2())
            s += "      Level 3: %d\n"%(self.get_EG_L3())
            s += "      Level 4: %d\n"%(self.get_EG_L4())
            s += "    Keyboard Level Scaling\n"
        return s

    # return all numeric operator data in a list
    def listData(self):
        l = []
        l.append(self.get_AMsens())
        l.append(self.get_oscillmode())
        l.append(self.getFrequency())
        l.append(self.get_detune() - 7)
        l.append(self.get_EG_R1())
        l.append(self.get_EG_R2())
        l.append(self.get_EG_R3())
        l.append(self.get_EG_R4())
        l.append(self.get_EG_L1())
        l.append(self.get_EG_L2())
        l.append(self.get_EG_L3())
        l.append(self.get_EG_L4())
        return l

    def getFrequency(self):
        if self.get_oscillmode() == 0:
            coarse = float(self.get_frequencyCoarse())
            if (coarse == 0):
                coarse = 0.5
            freq = coarse + (float(self.get_frequencyFine()) * coarse / 100)
        elif self.get_oscillmode() == 1:
            power = float(self.get_frequencyCoarse() % 4) + (float(self.get_frequencyFine()) / 100)
            freq = pow(10, power) 
        else:
            return -1
        return freq


    # DUMP AS BINARY
    def dump(self):
        return self.data



 
##################################################################################################################################

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
        return hashlib.md5(self.data[:118]).hexdigest()


    # Can pass a patch individually
    def __init__(self, data, index=-1):
        assert(len(data) == 128)
        self.index = index
        self.data = data[102:]
       # assert(len(self.data) == 26)
       
        i2 = 0
        self.operators = []
        # In the binary structure, operators are laid out in reverse order (so the first one is operator 6, etc.)
        # FIXME: does the order of operators affect equality? Suppose i have 2 operators: A, B. Does patch 1 (A,B) == patch 2 (B,A) ???
        for i1 in range(6):
            self.operators.append(Operator(data[i2:(i2 + 17)], (5 - i1)))
            i2 += 17


    def getComparableData(self):
        data = bytearray()
        for operator in self:
            data.extend(bytearray(operator.dump()))
        data.extend(bytearray(self.data[0:16]))
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

            #s += "%s"%(str(self))
            #s += Utils.safe_hexdump(self.data[0:102])
            #s += "\n"
                for operator in self:               
                    s += operator.prettyPrint(n)
                s += "\n  Patch Data:\n"
                s += "    " + Utils.safe_hexdump(self.data)
            s += "\n"
           # elif n == 2:
           #     s += "\n"

        elif n == 1:
            s += "Patch (voice) name: %s\n"%(self.get_name())
            s += "Patch (voice) number: %d\n"%(self.index + 1)
            s += "Algorithm: %d\n"%(self.get_algorithm())
            s += "Feedback: %d\n"%(self.get_feedback())
            s += "LFO\n"
            s += "  Wave: %s\n"%(LFOWaves.get(self.get_lfowave(), "Unknown LFO wave type"))
            s += "  Speed: %d\n"%(self.get_lfospeed())
            s += "  Delay: %d\n"%(self.get_lfodelay())
            s += "  Pitch Mod Depth: %d\n"%(self.get_lfopitchmoddepth())
            s += "  AM Depth: %d\n"%(self.get_lfoamdepth())
            s += "  Sync: %s\n"%(self.get_lfosync())
            s += "  Pitch Modulation Sensitivity: %d\n"%(self.get_lfopitchmodsens())
            s += "Oscillator Key Sync: %s\n"%(self.get_osckeysens())
            s += "Pitch Envelope Generator\n"
            s += "  Rate 1: %d\n"%(self.get_pitchEGR1())
            s += "  Rate 2: %d\n"%(self.get_pitchEGR2())
            s += "  Rate 3: %d\n"%(self.get_pitchEGR3())
            s += "  Rate 4: %d\n"%(self.get_pitchEGR4())
            s += "  Level 1: %d\n"%(self.get_pitchEGL1())
            s += "  Level 2: %d\n"%(self.get_pitchEGL2())
            s += "  Level 3: %d\n"%(self.get_pitchEGL3())
            s += "  Level 4: %d\n"%(self.get_pitchEGL4())
            s += "Transpose: %s\n"%(self.getTransposeStr())
            for operator in reversed(self.operators):
                s += "\n"
                s += operator.prettyPrint(n)
            s += "\n"

        #elif n == 2:
        #    s1 = "%s\n"%(self.get_name())
        #    if self.index >= 0:
        #        if self.index == 0:
        #            s += "" #"\n"
        #        s += "%d: %s"%((self.index + 1), s1)
        #    else:
        #        s += s1  #"\n" + s1

        return s
    
    # return all numeric patch data in a list
    def listData(self):
        l=[]
        l.append(self.get_algorithm())
        l.append(self.get_feedback())
        l.append(self.get_lfospeed())
        l.append(self.get_lfodelay())
        l.append(self.get_lfopitchmoddepth())
        l.append(self.get_lfoamdepth())
        l.append(int(self.get_lfosync()))
        l.append(self.get_lfopitchmodsens())
        l.append(self.get_pitchEGR1())
        l.append(self.get_pitchEGR2())
        l.append(self.get_pitchEGR3())
        l.append(self.get_pitchEGR4())
        l.append(self.get_pitchEGL1())
        l.append(self.get_pitchEGL2())
        l.append(self.get_pitchEGL3())
        l.append(self.get_pitchEGL4())
        for operator in reversed(self.operators):
            l.extend(operator.listData())

        return l


    def get_pitchEGR1(self):
        return int(Utils.safe_binascii_hexlify(self.data[0]), 16) 
    def get_pitchEGR2(self):
        return int(Utils.safe_binascii_hexlify(self.data[1]), 16) 
    def get_pitchEGR3(self):
        return int(Utils.safe_binascii_hexlify(self.data[2]), 16) 
    def get_pitchEGR4(self):
        return int(Utils.safe_binascii_hexlify(self.data[3]), 16) 
    def get_pitchEGL1(self):
        return int(Utils.safe_binascii_hexlify(self.data[4]), 16) 
    def get_pitchEGL2(self):
        return int(Utils.safe_binascii_hexlify(self.data[5]), 16) 
    def get_pitchEGL3(self):
        return int(Utils.safe_binascii_hexlify(self.data[6]), 16) 
    def get_pitchEGL4(self):
        return int(Utils.safe_binascii_hexlify(self.data[7]), 16) 

    def get_algorithm(self):
        return (int(Utils.safe_binascii_hexlify(self.data[8]), 16) & 0x1F) + 1 
    def get_feedback(self):
        return int(Utils.safe_binascii_hexlify(self.data[9]), 16) & 0x7  

    def get_lfowave(self):
        return (int(Utils.safe_binascii_hexlify(self.data[15]), 16) & 0xE) >> 1
    def get_lfospeed(self):
        return int(Utils.safe_binascii_hexlify(self.data[10]), 16) 
    def get_lfodelay(self):
        return int(Utils.safe_binascii_hexlify(self.data[11]), 16) 
    def get_lfopitchmoddepth(self):
        return int(Utils.safe_binascii_hexlify(self.data[12]), 16) 
    def get_lfoamdepth(self):
        return int(Utils.safe_binascii_hexlify(self.data[13]), 16) 
    def get_lfosync(self):
        return bool(int(Utils.safe_binascii_hexlify(self.data[14]), 16) & 0x1)
    def get_lfopitchmodsens(self):
        return (int(Utils.safe_binascii_hexlify(self.data[15]), 16) & 0xF0) >> 4   

    def get_osckeysens(self):
        return bool((int(Utils.safe_binascii_hexlify(self.data[9]), 16) & 0x8) >> 3)
    # FIX ME - is this correct? Isn't this is the start of the patch name?
    def get_transpose(self):
        return int(Utils.safe_binascii_hexlify(self.data[16]), 16)

    # Returns true if the 'name' region of the data (10 bytes) is UTF-8 decodable (?)
    def isNameUTF8(self):
        try:
            binascii.unhexlify(Utils.safe_binascii_hexlify(self.data[16:])).decode()
            return True
        except UnicodeDecodeError:
            return False

    def get_name(self):
        # Python 3 only:
        if sys.version_info >= (3,0):
            return binascii.unhexlify(Utils.safe_binascii_hexlify(str(self.data[16:]).encode().strip())).decode('unicode-escape')[2:-1]
#           return binascii.unhexlify(str(self.data[16:]))
        # Python 2 only:
        else:          
            return str(self.data[16:])
            # return binascii.hexlify(self.data[16:])       <--- returns the hex as a string

    def hasValidTranspose(self):
       if (self.get_transpose() >= 0) and (self.get_transpose() <= 48):
           return True
       return False

    def getTransposeStr(self):
       s = "out of range"
       if self.hasValidTranspose():
           return "%s%d"%(Notes.get((self.get_transpose() % 12), s), ((self.get_transpose() / 12) + 1))
       return s
       

    def hasASCIIname(self):
        #return all(ord(c) < 128 for c in str(self.data[16:]))
        if all(Utils.safe_ord(c) < 128 for c in str(self.data[16:])):       #  < 7f
            return True
        else:
            #print binascii.hexlify(self.data[16:])
            return False

    def hasFloatingEndMarker(self):

        # FIX ME ************************  DO THE SAME FOR OPERATOR AS WELL
        if sys.version_info >= (3,0):
            #   print(str(type(self.raw_endmarker)) + " and " + str(type(self.getValidEndmarker())))
          #  print(str(type(self.data[16:])))
            if all(b != 247 for b in self.data[16:]):       #  != F7 
                
                for operator in self:
                    if operator.hasFloatingEndMarker():
                        return True
                return False
            else:
                #print binascii.hexlify(self.data[16:])
                return True
        # FIX ME ************************

        else:
            #return all(ord(c) < 128 for c in str(self.data[16:]))
            if all(Utils.safe_ord(c) != 247 for c in str(self.data[16:])):       #  != F7
                for operator in self:
                    if operator.hasFloatingEndMarker():
                        return True
                return False
            else:
                #print binascii.hexlify(self.data[16:])
                return True

    #def hasPrintableName(self):
    #    pass


   
    # DUMP AS BINARY
    def dump(self):
        data = bytearray()
        for operator in self:
            data.extend(bytearray(operator.dump()))
        data.extend(bytearray(self.data))
        return bytes(data)


    # PARENT CLASS METHOD
    # 
    # Enumerate a list of unexpected field values
    def getUnexpectedFields(self):
        l = []
        if not self.hasValidTranspose(): 
           # seems to be a lot of deez:
           # l.append(VerifiableField.transpose)
            pass
        if not self.hasASCIIname():
            l.append(VerifiableField.patchname)
        if self.hasFloatingEndMarker():
            l.append(VerifiableField.floatingendmarker)
        return l
           



##################################################################################################################################


#        The structure of a valid Yamaha DX7 .syx binary is like this:
#
#        [F0 43 00 09 20 00] [patch 1] [patch 2] .... [patch 32] [XX] [F7]
#
#        Where:
#        [F0 43 00 09 20 00]    <--- header bytes
#        [patch]                <--- 128 bytes
#        [XX]                   <--- checksum
#        [F7]                   <--- end byte marker
#
#        So its total size is calculated like this:
#
#        6 + (32 * 128) + 2 = 4104 bytes
#
#        Here is info regarding the header:
#          
#        unsigned char sysexBeginF0;         // 0xF0
#        unsigned char yamaha43;             // 0x43
#        unsigned char subStatusAndChannel;  // 0
#        unsigned char format9;              // 9
#        unsigned char sizeMSB;              // 7 bits!  0x20
#        unsigned char sizeLSB;              // 7 bits!  0x00
#

# Yamaha DX7 .syx file containing 32 patches
class SysEx(object):

    def getType(self):
        return Synth.yamaha_dx7


    # IN: .syx binary or list of 32 patches
    def __init__(self, data):  

        self.patches = []

        
        if ((type(data) is str) or (type(data) is bytes)):
 
            # Python 2 will get 'str'
            # Python 3 will get 'bytes'
            
            assert(len(data) == 4104)

            #try:
            #    assert(len(data) == 4104)
            #except AssertionError as e:
                #e.args += ("Expected .syx data size: 4104 bytes (got %d bytes)"%(len(data)))
                #raise
            #    raise AssertionError("Expected .syx data size: 4104 bytes (got %d bytes)"%(len(data)))

            self.raw_header = data[0:6]
            self.raw_checksum = data[4102]
            self.raw_endmarker = data[4103]

           # try:
           #     assert(data[0:6] == self.getValidHeader())
           # except AssertionError as e:
                #e.args += ("Expected header: %s (got: %s)"%(self.getValidHeader(), binascii.hexlify(data[0:6])))
                #raise
           #     raise AssertionError("Expected header: %s (got: %s)"%(binascii.hexlify(self.getValidHeader()), binascii.hexlify(data[0:6])))
            # FIXME: raise AssertionError("Not a Yamaha DX7 compatible .syx file")       
 
            # The following should output 'f04300092000'
            #print binascii.hexlify(self.getValidHeader())
 
            
            i2 = 6
            for i1 in range(32):
                self.patches.append(Patch(data[i2:(i2 + 128)], i1))
                i2 += 128

        elif type(data) is list:

            assert(len(data) == 32)
            #self.patches = copy.copy(data)   #copy.deepcopy(data)
            
            self.patches = list(data)

            self.raw_header = self.getValidHeaders()[0]
            self.raw_checksum = binascii.unhexlify('%02x'%(self.calcChecksum()))
            self.raw_endmarker = self.getValidEndmarker()



    # PARENT CLASS METHOD
    # 
    # Enumerate a list of unexpected field values
    def getUnexpectedFields(self):
        l = []
        if not self.hasValidChecksum():
            l.append(VerifiableField.checksum)
        if not self.hasValidHeader():
            l.append(VerifiableField.header)
        if not self.hasValidEndmarker():
            l.append(VerifiableField.endmarker)
        if self.hasFloatingEndMarker():
            l.append(VerifiableField.floatingendmarker)
        return l

    #def __str__(self):
    #    return "Yamaha DX7"

    def __len__(self):
        return len(self.patches)
 
    def __iter__(self):
        return iter(self.patches)


    def prettyPrint(self, n=0):
        s = ""

        if n == 0:
            s += "Header: " + Utils.safe_hexdump(self.raw_header) + "\n\n"
            for patch in self:
                s += patch.prettyPrint(0) + "\n"
            s += "\nChecksum: "
            s += Utils.safe_hexdump(self.raw_checksum)
            s += "\nEnd marker: "
            s += Utils.safe_hexdump(self.raw_endmarker)
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
        if corrected:
            data = bytearray(self.getValidHeaders()[0])
        else:
            data = bytearray(self.raw_header)
        for patch in self:
            data.extend(bytearray(patch.dump()))
        if corrected:
            data.extend(bytearray(binascii.unhexlify('%02x'%(self.calcChecksum()))))
            data.extend(bytearray(b'\xF7'))
        else:
            data.extend(bytearray(self.raw_checksum))
            data.extend(bytearray(self.raw_endmarker))
        return bytes(data)

    # FIXME: need to check header, and end
    def hasFloatingEndMarker(self):
        for patch in self:
            if patch.hasFloatingEndMarker():
                return True
        return False



    def getValidEndmarker(self):
        return b'\xF7'

    def hasValidEndmarker(self):
        if sys.version_info >= (3,0):
            return bytes([self.raw_endmarker]) == self.getValidEndmarker()
        else:
            return self.raw_endmarker == self.getValidEndmarker()


    # A list of headers that are known to work
    def getValidHeaders(self):
        return [b'\xF0\x43\x00\x09\x20\x00', b'\xF0\x43\x00\x09\x10\x00']

    #def getExpectedHeader(self):
    #    return b'\xF0\x43\x00\x09\x20\x00'
        #F0 43 00 09 10 00

    def hasValidHeader(self):
   # def hasExpectedHeader(self):
        # Works in Python 2 (not sure about 3????):
        #print "The header on disk is: %s"%(binascii.hexlify(self.raw_header))

        # Python 3 only:
        if sys.version_info >= (3,0):
            #print "The expected header is: %s"%((hex(self.getExpectedHeader())[2:]).zfill(2))
            #return (ord(self.raw_header) == self.getExpectedHeader())
            return Utils.safe_ord(self.raw_header) in self.getValidHeaders()

        # Python 2 only:
        else:
            #print "The expected header is: %s"%()
            #return binascii.hexlify(self.raw_header) == binascii.hexlify(self.getExpectedHeader())
            return self.raw_header in self.getValidHeaders()


    # DEPRECATED : FIX ME
    # Expected checksum based on the algorithm we use.
    # The checksum is calculated over the 32 patch region (4096 bytes in size)
    def calcChecksumWork(self, patches):
        data = bytearray()
        for patch in patches:
            data.extend(bytearray(patch.dump()))
        checksum = int('00', 16)
        for i in range(len(data)):
            # This is a regular add (not a bit-wise one!)
            checksum += (data[i] & int('7F', 16))

        checksum = (~checksum) + 1;   
        checksum &= 0x7F;

        return checksum



    # Expected checksum based on the algorithm we use.
    # The checksum is calculated over the 32 patch region (4096 bytes in size)
    def calcChecksum(self):
        #return self.calcChecksumWork(self.patches)    
        data = bytearray()
        for patch in self:
            data.extend(bytearray(patch.dump()))
        checksum = int('00', 16)
        for i in range(len(data)):
            # This is a regular add (not a bit-wise one!)
            checksum += (data[i] & int('7F', 16))

        checksum = (~checksum) + 1;   
        checksum &= 0x7F;

        return checksum    

  #  def hasExpectedChecksum(self):
    def hasValidChecksum(self):
        #print "The checksum on disk is: %s"%(binascii.hexlify(self.raw_checksum))
        #print "The calculated checksum is: %s"%((hex(self.calcChecksum())[2:]).zfill(2))
        return (Utils.safe_ord(self.raw_checksum) == self.calcChecksum())
        

##################################################################################################################################


