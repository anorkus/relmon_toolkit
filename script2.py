"""
    Script to launch ValidationMatrix.py for downloaded RelVals in same directory
    & make dir2webdir so reports could be copied to /afs/../../../ReleaseMonitorig/

"""

import traceback
import os
import subprocess
import time

from progressbar import *
from multiprocessing.process import Process
from glob import glob

def progress():
    widgets = [FormatLabel('Working '), BouncingBar()]
    pbar = ProgressBar(widgets=widgets)
    for i in pbar(infinite_iterator()):
        time.sleep(.08)

def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

def validation_matrix(inputDir, outputDir, num_of_threads, HLT, logFile):
    if os.path.exists(inputDir):
        if HLT:
            params = ['ValidationMatrix.py', '-a', inputDir, '-o', outputDir, '--HLT', '--hash_name', '-N', num_of_threads]
        else:
            params = ['ValidationMatrix.py', '-a', inputDir, '-o', outputDir, '--hash_name', '-N', num_of_threads]
        logFile.write('###SubprocessParams: '+ ' '.join(params)+'\n')
        print " ".join(params)
        proc = subprocess.Popen(params, stdout=logFile)
        proc.wait()

def dir2web(inputDir, logFile):
    if os.path.exists(inputDir):
        params = ['dir2webdir.py', inputDir]
        logFile.write('###SubprocessParams: '+ ' '.join(params)+'\n')
        proc = subprocess.Popen(params)
        proc.wait()
    else:
        logFile.write('###dir2webdir: input Folder doesnt exist: '+inputDir+'\n')
        return False
    if not os.path.exists('BACK_PKLS'):
        os.mkdir('BACK_PKLS')
    params = 'mv *pkls* BACK_PKLS/'
    logFile.write('###SubprocessParams: '+ ' '.join(params)+'\n')
    proc = subprocess.Popen(params, shell=True)
    proc.wait()
    params = 'mv *back* BACK_PKLS/'
    logFile.write('###SubprocessParams: '+ ' '.join(params)+'\n')
    proc = subprocess.Popen(params, shell=True)
    proc.wait()

def do_some_work(element, logFile):
    print "### ", element
    __is_hlt = False
    __folder_name = element.split("_")

    if __folder_name[0] == "FullFastSim":
       folder_list = glob("rootFullFastSim*")
       for el in folder_list:
           CMSSW_rel = el.split('-')[1]
       __in_dir = "root"+__folder_name[0]+"-"+CMSSW_rel
       __out_dir = CMSSW_rel+"_FullSimFastSimReport"
    else:
        __in_dir = "root" + __folder_name[0]
        __out_dir = __folder_name[0] + "Report"

    if "PU" in __folder_name:
        __in_dir += "PU"
        __out_dir += "_PU"
    if "HLT" in __folder_name:
        __out_dir += "_HLT"
        __is_hlt = True

    validation_matrix(__in_dir, __out_dir, '6', __is_hlt, logFile)
    dir2web(__out_dir, logFile)


if __name__ == '__main__':
    start_time = time.time()
    proc = Process(target=progress)
    if(os.path.exists('validationLog.log')):
        print "Log File exists. Making new one"
        os.remove('validationLog.log')
    logFile = open('validationLog.log', 'a')  #open a log file for output -> in case it already exists delete old one?
    try:
        TO_DO = ["Data", "Data_HLT", "FullSim", "FullSim_HLT", "FullSim_PU",
                "FullSim_PU_HLT", "FastSim", "FastSim_HLT", "FastSim_PU",
                "FastSim_PU_HLT", "FullFastSim", "FullFastSim_HLT", "Generator"]

        proc.start()
        for i in TO_DO:
            do_some_work(i, logFile)

        #Do some work here
        proc.terminate()
        logFile.close()
        #os.system("echo 'Done.\nElapsed time:\n"+secondsToStr(time.time() - start_time)+"' | mail -s 'RelMon\n' 0041767098127@mail2sms.sunrise.ch")
        os.system("echo 'Done.\nElapsed time:\n%s' | mail -s 'RelMon' +41767098127@mail2sms.cern.ch" %(secondsToStr(time.time() - start_time)))
    except SystemExit:
        os.system("echo 'Error' | mail -s 'RelMon' +41767098127@mail2sms.cern.ch")
        sys.exit()
    except:
        proc.terminate()
        print "\n"
        print "Error in main script"
        print traceback.format_exc()
        os.system("echo 'Error' | mail -s 'RelMon' +41767098127@mail2sms.cern.ch")
