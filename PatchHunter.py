# REQUIREMENTS:
#
# https://bitbucket.org/techtonik/hexdump/ 
# $ pip install hexdump
#

#from yamahadx7_syx import SysEx as YamahaDX7syx
#from yamahadx7_syx import Patch as YamahaDX7patch
import yamahadx7_syx
import rolandjx8p_syx
import yamahatx802_syx
import os
import binascii
import hexdump
import hashlib
from EnumTypes import Synth as Synth
from EnumTypes import Bank as Bank
#from EnumTypes import VerifiableField as VerifiableField
import Utils
from glob import glob


class PatchHunter(object):


    def genSysex(self):

        l = []
        
        if self.bank == Bank.patch:
                      
            if self.synth == Synth.yamaha_dx7:
                TargetModule = yamahadx7_syx
                sysex_patch_count = 32

            elif self.synth == Synth.yamaha_tx802:
                TargetModule = yamahatx802_syx
                sysex_patch_count = 32
                
            elif self.synth == Synth.roland_jx8p:
                #TargetModule = rolandjx8p_syx
                #sysex_patch_count = 64    # FIX ME
                pass

            sysex_count = len(self) / sysex_patch_count
            leftover_patch_count = len(self) % sysex_patch_count


            #print "Number of sysex i could generate: %d"%(sysex_count)
            #print "Leftover patches: %d"%(leftover_patch_count)

            sysex_l = []
            leftover_patch_l = []
            curr_patch_count = 0
            curr_sysex_count = 0
            for obj in self:

                filename = obj[0]
                patch = obj[1]

                if curr_sysex_count == sysex_count:
                    print ("WARNING: orphaning patch: %s"%(filename))
                    leftover_patch_l.append(patch)
                else:
 
                    if curr_patch_count == 0:
                        patches = []

                    patches.append(patch)
                    curr_patch_count += 1
     
                    if (curr_patch_count % sysex_patch_count) == 0:
                        # init new sysex
                        new_sysex = TargetModule.SysEx(patches)                     
                        sysex_l.append(new_sysex)

                        curr_sysex_count += 1
                        curr_patch_count = 0

                        
                        

            # FIX ME: remove once done
            assert(len(sysex_l) == sysex_count)
            assert(len(leftover_patch_l) == leftover_patch_count)
 
            l.append(sysex_l)
            l.append(leftover_patch_l)

        return l
 


    def searchByName(self, s):
        hits = []
        i = 0
        for obj in self:
            filename = obj[0]
            blob = obj[1]
            if self.bank == Bank.sysex:
                l = blob.getPatchesByName(s)
                for p in l:
                    hits.append([(i + 1), filename, str(p)])
            elif self.bank == Bank.patch:
                try:
                    if s.lower() in str(blob).lower(): 
                        hits.append([(i + 1), filename, str(blob)])
                except UnicodeDecodeError as e:
                    continue
            i += 1
        
        return hits
                    

    
    def __len__(self):
        return len(self.enumerated)

    def __iter__(self):
        return iter(self.enumerated)

    # Returns a list of possibly dodgy patches
    def getDodgy(self):
        l1 = []
        i = 0
        for b in self:
            #filename = b[0]
            #blob = b[1]

            l2 = b[1].getUnexpectedFields()
            if len(l2) > 0:
                l1.append([i, b, l2])   # [index, blob, unexpected fields list]

            i += 1
        return l1

    # Files that could not be opened (OS reasons)
    def getFailedCount(self):
        return len(self.could_not_open)

    # Files that could not be parsed
    def getInvalidCount(self):
        return len(self.could_not_parse)
        

    def __init__(self, inputdir, synth, bank): 

        self.inputdir = inputdir
        self.synth = synth
        self.bank = bank

        self.enumerated = []
        self.could_not_open = []
        self.could_not_parse = []

        self.patch_count = 0
        self.unique_patches = {}

        # Recursively enumerate all target file types below input directory
        fn_l = [y for x in os.walk(inputdir) for y in glob(os.path.join(x[0], '*.%s'%(Utils.exts_dict[bank])))]
        for fn in fn_l:
            #print fn
            try:
                f1 = open(fn, "rb")
                data = f1.read()
                f1.close()
            except IOError:
                #print("WARNING: could not open: %s (skipping)\n"%(fn))
                self.could_not_open.append(fn)

            md5 = hashlib.md5(data).hexdigest()

            try:

                obj = None

                if synth == Synth.yamaha_dx7:
                    TargetModule = yamahadx7_syx
                elif synth == Synth.roland_jx8p:
                    TargetModule = rolandjx8p_syx
                elif synth == Synth.yamaha_tx802:
                    TargetModule = yamahatx802_syx

                if bank == Bank.sysex:
                    obj = TargetModule.SysEx(data)  
                    for patch in obj:
                        if patch.getHash() not in self.unique_patches:
                            self.unique_patches[patch.getHash()] = patch
                        self.patch_count += 1
                        
                elif bank == Bank.patch:
                    obj = TargetModule.Patch(data)
                    if obj.getHash() not in self.unique_patches:
                        self.unique_patches[obj.getHash()] = obj
                    self.patch_count += 1

                if obj is not None:
                    self.enumerated.append([fn, obj])


                #md5_gen = hashlib.md5(syx.dump()).hexdigest()
        

               # if md5_input != md5_gen:
                    # The way the .syx actually is on disk, and the way we regenerate it programmatically, results in different binaries!
                    # Likely culprits: checksum, .. FIXME
               #     if not syx.hasValidChecksum():
               #         print "The checksum on disk is: %s"%(binascii.hexlify(syx.raw_checksum))
               #         print "The calculated checksum is: %s"%((hex(syx.getChecksum())[2:]).zfill(2))
               #         raise AssertionError(".syx checksum error!")

               # for patch in syx:
               #     if patch.getHash() in patch_md5:
                        #print "Already have a patch that matches: %s"%(patch.get_name())
               #         pass
               #     else:
               #         print "Found new patch: %s"%(patch.get_name())
               #         patch_md5.append(patch.getHash())
               #         try:
               #             f2 = open("%s/%s.patch"%(opts.outputdir, patch.getHash()), "wb")
               #             f2.write(patch.dump())
               #             f2.close()
               #         except IOError:
               #             print("Error: could not write: %s/%s.patch\n"%(opts.outputdir, patch.getHash()))
               #             exit(-1)

        

                #print "Success: %s"%(fn)

    

            except AssertionError as e:
                #print str(e)
                #print "WARNING: skipping: %s\n"%(fn)
                #skipped_syx_count += 1
                self.could_not_parse.append(fn)

