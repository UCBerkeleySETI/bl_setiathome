#!/usr/bin/env python
#plot_coarse_channel.py fnameIN fFreq fnameOUT
import time
start_time = time.time()
import glob
import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import pdb
import cProfile

import requant_utils

if len(sys.argv) != 4:
        print '\nmissing information\n'
        print 'usage is:\n'
        print '''plot_coarse_channel.py fnameIN fFreq fnameOUT'''
        sys.exit()

fileinit = str(sys.argv[1])
fFreq = float(sys.argv[2])
fileout = str(sys.argv[3])

if (fileinit[-4:] == '.raw'):
        fileinit = fileinit.replace(fileinit[len(fileinit)-8:],"*.raw")
else:
        print 'enter raw file name\n'
        sys.exit()

print fileinit
all_filenames = sorted(glob.glob(fileinit))
# print all_filenames
print all_filenames

fname = all_filenames[0]
fread = open(fname,'rb')        # open first file of data set
currline = str(fread.read(80))          # reads first line
nHeaderLines = 1
while currline[0:3] != 'END':           # until reaching end of header
        currline = str(fread.read(80))  # read new header line
        # print currline
        if currline[0:9] == 'PKTSIZE =':        # read packet size
                nPktSize = float(currline[9:])
        if currline[0:9] == 'OBSFREQ =':        # read cenral frequency
                cenfreq = float(currline[9:])
        if currline[0:9] == 'OBSBW   =':        # read bandwidth
                obsbw = float(currline[9:].split("'")[1])
        if currline[0:9] == 'OBSNCHAN=':        # read number of coarse channels
                obsnchan = float(currline[9:].split("'")[1])
        if currline[0:9] == 'DIRECTIO=':        # read directio flag
                ndirectio = float(currline[9:].split("'")[1])
        if currline[0:9] == 'BLOCSIZE=':        # read block size
                nblocsize = float(currline[9:])
        nHeaderLines = nHeaderLines + 1         # counts number of lines in header

fread.close()

nChanSize = int(nblocsize / obsnchan)
nPadd = 0
if ndirectio == 1:
        nPadd = int((math.floor(80.*nHeaderLines/512.)+1)*512 - 80*nHeaderLines)
statinfo = os.stat(fname)
NumBlocs = int(round(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines)))

fLow = cenfreq - obsbw/2.
fHigh = cenfreq + obsbw/2.
dChanBW = obsbw/obsnchan

if fFreq < min(fLow,fHigh) or fFreq > max(fLow,fHigh):
                print 'Frequency not covered by file\n'
                print 'Frequency bandwidth = ['+str(min(fLow,fHigh))+','+str(max(fLow,fHigh))+']\n'
                sys.exit()

if obsbw > 0:
                nChanOI = int((fFreq-fLow)/dChanBW)
else:
                nChanOI = int((fLow-fFreq)/abs(dChanBW))

BlocksPerFile = np.zeros(len(all_filenames))
idx = 0
for fname in all_filenames:
        statinfo = os.stat(fname)
        BlocksPerFile[idx] = int(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines))
        idx = idx+1

NumBlockTotal = int(sum(BlocksPerFile))
NewTotBlocSize = int(NumBlockTotal * nChanSize)

fLowChan = fLow + (nChanOI)*dChanBW
fHighChan = fLowChan + dChanBW
TotCenFreq = (fLowChan+fHighChan)/2.

idx = -1
CurrBlkIdx = -1
output_file = open(fileout,'wb')
for fname in all_filenames:
        idx = idx+1
        fread = open(fname,'rb')        # open first file of data set
        for nblock in range(int(BlocksPerFile[idx])):
                CurrBlkIdx = CurrBlkIdx + 1
                print 'processing block #' + str(CurrBlkIdx+1) + '/' + str(NumBlockTotal)
                fread.seek(int(nblock*(80*nHeaderLines+nPadd+nblocsize)))       # goes to the header
                currline = fread.read(80)
                output_file.write(currline)
                while str(currline[0:3]) != 'END':              # until reaching end of header
                        currline = fread.read(80)               # read new header line
                        if str(currline[0:9]) == 'OBSFREQ =':   # change central frequency value
                                NewVal = TotCenFreq
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'OBSBW   =':   # change bandwidth value
                                NewVal = dChanBW
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'OBSNCHAN=':   # change number of coarse channels
                                NewVal = 1
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'DIRECTIO=':   # change directio value
                                NewVal = 0
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'BLOCSIZE=':   # change block size value
                                NewVal = int(nChanSize)
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'NPKT    =':
                                NewVal = int(NewTotBlocSize/nPktSize)
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'PKTIDX  =':
                                NewVal = CurrBlkIdx * (nChanSize/nPktSize)
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        if str(currline[0:9]) == 'PKTSTOP =':
                                NewVal = int(NewTotBlocSize/nPktSize)
                                NewValStr = str(NewVal)
                                if len(NewValStr) > 20:
                                        NewValStr = NewValStr[0:20]
                                teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
                                teststr = teststr + ' '*(80-len(teststr))
                                currline = teststr
                        output_file.write(currline)
                fread.seek(nblock*(nHeaderLines*80+nPadd+nblocsize)+nHeaderLines*80+nPadd+nChanOI*nChanSize)

                # Read data, setup input and output arrays
                in_8i  = np.fromfile(fread, count=int(nChanSize), dtype='int8')
                out_2u = np.zeros(in_8i.shape[0] / 4, dtype='uint8')
               
                # Run requantization C++ code
                requant_utils.requant_8i_2u(in_8i, out_2u)
                
                # Write to file
                out_2u.tofile(output_file)
#               pdb.set_trace()

                #output_file.write(bitted_string)        # write data block
        fread.close()                   # close current file

output_file.close()
print("--- %s seconds ---" % (time.time() - start_time))
