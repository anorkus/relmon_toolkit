"""
    Script to download root files from DQM offline GUI and sort them in directories
"""

import optparse
import logging
import logging.handlers
import subprocess
import os
import glob
import time

from progressbar import *
from multiprocessing.process import Process
import sys
import time
import traceback

def launch_subprocess(params, logFile):
    proc = subprocess.Popen(params, shell=True, stdout=logFile)
    proc.wait()

def download_files(release, regexp, mthreads, logFile, only_Data, only_MC):
    if not only_MC:
        logFile.write("Download Data files for CMSSW release: "+ release+"\n")
        logFile.flush()
        ###download DATA RelVals
        if options.dry_run == True:
            params = ["fetchall_from_DQM_v2.py","-d","-r", release, "-e", regexp, "--mthreads", mthreads, "--dry"]
            proc = subprocess.Popen(params, stdout=logFile) #launch a subprocess in same shell as python has been launched
            proc.wait()   #wait until 
        else:
            params = ["fetchall_from_DQM_v2.py","-d","-r", release, "-e", regexp, "--mthreads", mthreads]
            proc = subprocess.Popen(params, stdout=logFile) #launch a subprocess in same shell as python has been launched
            proc.wait()   #wait until 
            ###Move data files to rootData folder
            if not  os.path.exists("rootData"):
                os.mkdir("rootData")
            params = ["mv DQM* rootData/"]
            launch_subprocess(params, logFile)
            
    ####DOWNLOAD MC files ## 
    if not only_Data:
        logFile.write("Download MC files for CMSSW release: "+ release+"\n")
        logFile.flush()
        if options.dry_run == True:
            params = ["fetchall_from_DQM_v2.py","-m","-r", release, "-e",regexp, "--mthreads", mthreads, "--dry"]
            proc = subprocess.Popen(params, stdout=logFile) #launch a subprocess in same shell as python has been launched
            proc.wait()   #wait until 
        else:
            params = ["fetchall_from_DQM_v2.py","-m","-r", release, "-e", regexp, "--mthreads", mthreads]
            proc = subprocess.Popen(params, stdout=logFile) #launch a subprocess in same shell as python has been launched
            proc.wait()   #wait until 
                    
            ##Move files to rootFASTSIM_PU folder
            if len(glob.glob('*PU*')) != 0:     #check (count) PU files in directory: if they exist then create folders and move them, else skip (not creating empty dirs)
                logFile.write("Moving files to rootFastSimPU folder for: "+ release+"\n")
                logFile.flush()
                if not  os.path.exists("rootFastSimPU"):
                    os.mkdir("rootFastSimPU")
                #print os.listdir(os.getcwd())
                params = ["mv DQM*PU*FastSim* rootFastSimPU/"]
                logFile.write("%s\n" %("".join(params)))
                logFile.flush()
                launch_subprocess(params, logFile)
                ##Move files to rootFULLSIM_PU folder
                logFile.write("Moving files to rootFullSimPU folder for: "+ release+"\n")
                logFile.flush()
                if not  os.path.exists("rootFullSimPU"):
                    os.mkdir("rootFullSimPU")
                params = ["mv DQM*PU* rootFullSimPU/"]
                logFile.write("%s\n" %("".join(params)))
                logFile.flush()                
                launch_subprocess(params, logFile)
            ##Move files to rootFASTSIM folder
            logFile.write("Moving files to rootFastSim folder for: "+ release+"\n")
            logFile.flush()
            if not  os.path.exists("rootFastSim"):
                os.mkdir("rootFastSim")
            params = ["mv DQM*FastSim* rootFastSim/"]
            logFile.write("%s\n" %("".join(params)))
            logFile.flush()
            launch_subprocess(params, logFile)
            ##Move files to rootGenerator folder
            logFile.write("Moving files to rootGenerator folder for: "+ release+"\n")
            logFile.flush()
            if not  os.path.exists("rootGenerator"):
                os.mkdir("rootGenerator")
            params = ["mv DQM*_gen* rootGenerator/"]
            logFile.write("%s\n" %("".join(params)))
            logFile.flush()
            launch_subprocess(params, logFile)
            ##Move files to rootFullSim folder
            logFile.write("Moving files to rootFullSim folder for: "+ release+"\n")
            logFile.flush()
            if not  os.path.exists("rootFullSim"):
                os.mkdir("rootFullSim")
            params = ["mv DQM* rootFullSim/"]
            logFile.write("%s\n" %("".join(params)))
            logFile.flush()
            launch_subprocess(params, logFile)

def make_symlinks(dry_run, newest_release, logFile):
    ##Make symlinks for FullSimFastSim report\
    logFile.write("Making symlinks to rootFullFastSim folder\n")
    logFile.flush()
    if dry_run != True:
        if not  os.path.exists("rootFullFastSim"+"-"+newest_release):
            os.mkdir("rootFullFastSim"+"-"+newest_release)
        os.chdir("rootFullFastSim"+"-"+newest_release)
        params = ["ln -s ../rootFullSim/*"+newest_release+"* ."]
        launch_subprocess(params, logFile)
        params = ["ln -s ../rootFastSim/*"+newest_release+"* ."]
        launch_subprocess(params, logFile)

def progress():
    widgets = [FormatLabel('Working '), BouncingBar()]
    pbar = ProgressBar(widgets=widgets)
    for i in pbar(infinite_iterator()):
        time.sleep(.08)
        
if __name__ == "__main__":
    try:
        proc = Process(target=progress)
        ###Parse command line arguments
        parser = optparse.OptionParser("Usage: %prog [options]")
        parser.add_option("-r", "--release", action="store", dest="release", help="Releaseto download. Format CMSSW_x_y_z.", metavar="RELEASE")
        parser.add_option("--re1", "--regexp1", action="store", default="", dest="regexp", help="Comma separated regular expresions for file names.", metavar="REGEXP")
        parser.add_option("--re2", "--regexp2", action="store", default="", dest="regexp2", help="Comma separated regular expresions for file names.", metavar="REGEXP")
        parser.add_option("--mthreads", action="store", default="3", dest="mthreads", help="Number of paralel threads to download files. Default is 3.", metavar="MTHREADS")
        parser.add_option("--dry", action="store_true", default=False, dest="dry_run", help="Show which file list which to be downloaded, but do not download themm. T.y. dry run of script.")
        parser.add_option("-d", '--data', action="store_true", default=False, dest="dwnld_data", help="Set to download only DATA RelVals.")
        parser.add_option("-m", '--mc', action="store_true", default=False, dest="dwnld_MC", help="Set to download only Monte Carlo RelVals.")
        ###end of command line parsing
        
        if(os.path.exists('downloadLog.log')):
            print "Log File exists. Making new one"
            os.remove('downloadLog.log')
        logFile = open('downloadLog.log', 'a')  #open a log file for output -> in case it already exists delete old one?
        
        (options, args) = parser.parse_args()
        print options.release.split(','), options.regexp,options.regexp2, options.mthreads, options.dry_run
        regexps = []
        regexps.append(options.regexp)
        regexps.append(options.regexp2)
        releases = options.release.split(',')
        #releases.remove('') #remove empty values -> in case user gives CMSSW_x_y_z, as parameter
        if len(releases) != 2:
            print "Error. You must specify 2 releases for comparison"
        else:
            newest_release = max(options.release.split(','))  #find newest release (with top number)
            proc.start()
            i = 0 
            for release in releases:
                download_files(release, regexps[i], options.mthreads, logFile, options.dwnld_data, options.dwnld_MC)
                i = i + 1
            make_symlinks(options.dry_run, newest_release, logFile)

            proc.terminate()
            logFile.close()
    except SystemExit:
        sys.exit()  
    except:
        proc.terminate()
        print "\n"
        print "Error in main script"
        print traceback.format_exc()
