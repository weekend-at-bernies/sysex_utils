# REQUIREMENTS:
#
# $ pip install enum34
#


import Settings
from enum import Enum 

class Synth(Enum):
    yamaha_dx7 = "Yamaha DX7"
    roland_jx8p = "Roland JX-8P"
    yamaha_tx802 = "Yamaha TX802"
    yamaha_tx81z = "Yamaha TX81z"
 

class FileType(Enum):
    # Sysex consists of multiple patches
    sysex = Settings.sysex_file_extension
    # Single patch
    patch = Settings.patch_file_extension


class Bank(Enum):
    voice = "voice"
    performance = "performance"



class VerifiableField(Enum):
    floatingendmarker = "floating end marker byte: 0xF7"
    checksum = "invalid checksum"
    header = "invalid header"
    endmarker = "invalid endmarker"
    transpose = "unexpected transpose value"        # Refer: yamahadx7_syx.py:Patch:hasValidTranspose()
    patchname = "non-ascii value(s) in patch name"   
    incorrectsize = "incorrect file size"           # eg. yamaha dx7 .syx should be 4104 bytes    




