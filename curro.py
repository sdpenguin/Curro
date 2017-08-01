#!/usr/bin python

import sys
import subprocess
import glob
import os
import signal
import pexpect
import time
import argparse

import configParse
import sshCommands

#DEFAULT Variables (examples) - should change either here, or preferably in config
#TODO: move to config.txt and parse
HOST="root@10.1.194.69"
curroPath = "" #You can set to something other than Null to force curro to use a different working directory to that curro.py is in
reventPath = "/data/Software/workload-automation/wlauto/common/bin/armeabi/revent"
targetReventPath = "/mnt/stateful_partition/apps"
waPath = "/usr/local/bin/wa"

def main():
    parser = argparse.ArgumentParser(description="Tool for automating revent recordings and replays using workoad automation.")
    subparsers = parser.add_subparsers(dest="subparser_name", help="You can record and then either wareplay or replay")
    record_parser = subparsers.add_parser('record', help='Record actions on a remote device into a revent file')
    record_parser.add_argument('--timeout', '-t', help="Timeout for recording. Default = 3 seconds", required=False, default=3)
    record_parser.add_argument('--output', '-o', help="Optional file name for output, otherwise automatically named", required=False, default=None)
    record_parser.add_argument('--setup', '-s', help="Record a setup revent")
    record_parser.add_argument('--close', '-c', help="Record a close revent") #TODO: implement setup and close
    replay_parser = subparsers.add_parser('replay', help='Replay a revent file')
    replay_parser.add_argument('file', help="File to be replayed")
    wareplay_parser = subparsers.add_parser('wareplay', help='Replay a revent file using wa, for example to use instruments to monitor the processors')
    wareplay_parser.add_argument('file', help="File to be replayed") #TODO: if a text file then play for all revents in file
    wareplay_parser.add_argument('agenda', help="WA agenda to use")
    wareplay_parser.add_argument('--idletime', '-i', help="Time to remain idle in after setup", required=False, default=10)
    
    args = parser.parse_args()

    global curroPath
    if(curroPath==""): #Will use the curro working directory if not otherwise specified
    #To use your own directory (specified above), you must have a configuration folder and its files, a wa folder and a revents folder
        curroPath = str(sys.path[0])

    #Pull variables from config file:
    configReturns = configParse.configParse(curroPath,"HOST","reventPath","targetReventPath","waPath") #Note that configParse always returns configReturns[0] as [0,False] (for debugging),
    #so numbering starts at 1
    HOST = configReturns[1][0]
    reventPath = configReturns[2][0]
    targetReventPath = configReturns[3][0]
    waPath = configReturns[4][0]

    configReturns = [[0,False],]

    if(args.subparser_name=="record"):
        if(args.output!=None):
            record(configReturns, timeout = vars(args)['timeout'], setup=vars(args)['setup'], close=vars(args)['close'], outputName= vars(args)['output'])
        else:
            configReturns = configParse.configParse(curroPath,"captureCount")
            record(configReturns, timeout = vars(args)['timeout'], setup=vars(args)['setup'], close=vars(args)['close'])
    elif(args.subparser_name=="replay"):
        replay(fileName=vars(args)['file'])
    elif(args.subparser_name=="wareplay"):
        if((str(args.file)).endswith(".txt")): #You may also specify a text file containing a list of revent recordings
            reventList = open(str(curroPath)+"/configuration/"+ str(vars(args)['file']), "r")
            for revent in reventList:
                if(str(revent).startswith("idle:")):
                    for revent in reventList:
                        configReturns = configParse.configParse(curroPath,"waCount",str(revent).strip())
                        wareplay(configReturns,fileName=str(revent).strip(),waAgendaFile=vars(args)['agenda'], idleMode=True, idleTime=vars(args)['idletime'])#TODO: Idle time)
                    break
                else:
                    configReturns = configParse.configParse(curroPath,"waCount",str(revent).strip())
                    wareplay(configReturns,fileName=str(revent).strip(),waAgendaFile=vars(args)['agenda'])
        else:
            configReturns = configParse.configParse(curroPath,"waCount",str(vars(args)['file']))
            wareplay(configReturns,fileName=vars(args)['file'],waAgendaFile=vars(args)['agenda'])

def record(configReturns, timeout, setup, close, **kwargs):
    if(setup!=None):
        listOfSuffixes = ['.setup','']
    else:
        listOfSuffixes = ['',]
    if(close!=None):
        listOfSuffixes.append('.close')
    for item in listOfSuffixes:
        var = raw_input("\nPress enter when you are ready to begin recording the " + ("setup" if str(item) == ".setup" else ("main recording" if str(item) == "" else "close"))) + "revent file\n"
        #create a directory for recorded events files
        sshCommands.localCommand("cd "+curroPath+" cd revents || (cd "+curroPath+" mkdir revents; cd revents;)")

        print "Moving revent"
        sshCommands.scp(str(curroPath)+"/external/revent/revent",targetReventPath+"/revent")

        #Note, timeout is a number of seconds after the user stops input. For more info: revent.c
        print "Starting revent"
        PROCESS = targetReventPath+"/revent"
        OPTIONS = "record /tmp/reventOutput -t " + str(timeout)
        sshCommands.sshProcess(HOST, PROCESS, OPTIONS)

        if('outputName' in kwargs): #if a file name is specified
            if(os.path.isfile(str(curroPath)+"/revents/"+str(kwargs['outputName'])+str(item))):
                var = raw_input("File exists, overwrite (y/n)?")
                if "y" in var:
                    sshCommands.localCommand("scp "+HOST+":/tmp/reventOutput "+str(curroPath)+"/revents/"+str(kwargs['outputName'])+str(item))
                    print "Output to file: " + str(kwargs['outputName']) + str(item)
                    continue
                else:
                    configReturns = configParse.configParse(curroPath,"captureCount")
                    sshCommands.localCommand("scp "+HOST+":/tmp/reventOutput "+str(curroPath)+"/revents/reventOutput-"+str(configReturns[1][0])+str(item))
                    print "Output to file: reventOutput-" + str(int(configReturns[1][0])) + str(item)
                    continue
            sshCommands.localCommand("scp "+HOST+":/tmp/reventOutput "+str(curroPath)+"/revents/"+str(kwargs['outputName'])+str(item))
            print "Output to file: " + str(kwargs['outputName'])+str(item)
            continue
        else: #Otherwise automatically name
            sshCommands.localCommand("scp "+HOST+":/tmp/reventOutput "+str(curroPath)+"/revents/reventOutput-"+str(configReturns[1][0]) + str(item))
            print "Output to file: reventOutput-" + str(int(configReturns[1][0])) + str(item)
            continue
    
def replay(fileName):
    sshCommands.scp(str(curroPath)+"/revents/"+fileName,targetReventPath+"/replayFile") #moves the file to the remote server
    sshCommands.sshProcess(HOST,targetReventPath+"/revent","replay "+targetReventPath+"/replayFile") #replays the file
    
def wareplay(configReturns, fileName, waAgendaFile, idleMode=False, idleTime=10):
    agendaPath = str(waAgendaFile)
    
    agendaFileObject = open(str(curroPath)+"/configuration/"+waAgendaFile, "r")
    agendaFileText = agendaFileObject.read()

    foundIdleTime = False
    agendaFileObject.seek(0)
    for line in agendaFileObject:
        if("workloads:" in str(line)):
            for line in agendaFileObject:
                if("reventFileName:" in str(line)):
                    agendaFileText = agendaFileText.replace(str(line).strip(), "reventFileName: " + '"' + fileName + '"')
                elif("reventFilePath:" in str(line)):
                    agendaFileText = agendaFileText.replace(str(line).strip(), "reventFilePath: " + '"' + curroPath + '/revents/' + '"')
                #Add support here for new types of workloads in the revent.txt file
                elif("name:" in str(line) and idleMode==True):
                    agendaFileText = agendaFileText.replace(str(line).strip(), "name: "+'"'+ "idleRevent" + '"')
                elif("name:" in str(line) and idleMode==False):
                    agendaFileText = agendaFileText.replace(str(line).strip(), "name: "+'"'+"basicRevent"+'"')
                elif("idletime:" in str(line)):
                    if(idleMode==True):
                        agendaFileText = agendaFileText.replace(str(line).strip(), "idletime: "+str(idleTime))
                        foundIdleTime = True
                    else:
                        agendaFileText = agendaFileText.replace(str(line), "")
            if(foundIdleTime == False and idleMode==True):
                agendaFileText = agendaFileText + "                idletime: " + str(idleTime)
            break

    agendaFileObject.close()
    agendaFileObject = open(str(curroPath)+"/configuration/"+waAgendaFile, "w+")
    agendaFileObject.write(agendaFileText)
    agendaFileObject.close()
    
    #ADD VERBOSE -v AS OPTION BELOW FOR WA VERBOSE or in future add as a cmd line option
    #A workload can run in both idle mode and ordinary mode
    try:
        sshCommands.localCommand('cd '+str(curroPath)+'/wa; wa run ../configuration/'+waAgendaFile+' -v -d '+fileName+"-"+str(configReturns[2][0])+ (".idle" if idleMode==True else ""))
    except:
        print "The reventRecording " + str(fileName) + " wa run was NOT successfully completed..."

if __name__ == "__main__": main()
