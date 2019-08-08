#import os
#import sys
#import binascii
#import hashlib
#import Utils
#import copy
#from EnumTypes import Synth as Synth
#from EnumTypes import VerifiableField as VerifiableField
import yamahadx7_syx

# REFERENCES:
# ?


raw_sysex_data_len = 5239
preamble_data_len = 1135
sysex_patch_count = 32


##################################################################################################################################


# .syx is a bank of 32 voice patches
# It is 5239 bytes length and structured as such:
#  [ 1135 bytes of preamble ] [ 4104 bytes of DX7 sysex ]
#
# So essentially a TX802 32 voice/patch bank .syx is SAME as a DX7 with some
# extra 1135 bytes of crap at the front. Check out: 'tx802_voice_syx_preamble.bin'
# to see it.
class SysEx(object):


    def get(self):
        return self.sysex

    # IN: .syx binary or list of 32 patches
    def __init__(self, data):  
        
        if ((type(data) is str) or (type(data) is bytes)):
 
            # Python 2 will get 'str'
            # Python 3 will get 'bytes'
            
            assert (len(data) == raw_sysex_data_len), "Expected %d bytes, got: %d"%(raw_sysex_data_len, len(data))

            self.sysex = yamahadx7_syx.SysEx(data[preamble_data_len:])

 

        elif type(data) is list:

            assert(len(data) == sysex_patch_count)
            self.sysex = yamahadx7_syx.SysEx(data)


##################################################################################################################################

