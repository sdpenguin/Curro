import sys
import subprocess
import glob
import os

#Default Variables
HOST="root@10.1.194.69"
COMMAND = ""
PROCESS = ""
OPTIONS = ""
reventPath = "/data/Software/workload-automation/wlauto/common/bin/armeabi/revent"
targetReventPath = "/mnt/stateful_partition/apps/revent"
waPath = "/usr/local/bin/wa"
waOption = "run"

#######FUNCTIONS#################

def sshCommand(command = COMMAND, host=HOST):
	command = "'" + command + "'" #automatic quotes around command so that they can be input in same format as local commands
	output = subprocess.check_output("ssh " + HOST + " " + command, shell=True)
	print output
	print "Successfully executed remote command on "+ host # + " :" + command

def sshProcess(host = HOST, processName = targetReventPath, options = ""):
	print "Executing " + processName + " on " + host + " with options: " + options
	output = subprocess.call(["ssh", HOST, processName, options])
	print "Finished executing remote process" + processName

def scp(localdir,remotedir,host=HOST):
	COMMAND = "scp "+localdir+" "+host+":"+remotedir
	localCommand(COMMAND)

def localCommand(command):
	output = subprocess.check_call(command, shell=True)
	print output
	print "Successfully executed local command" # + ": " + command

def runFile(fileName="", remote = False, host = HOST):
	openedFile = open(fileName,"r")
	contents = openedFile.read()
	if(remote==False):
		localCommand(contents)
	else:
		sshCommand(command, host)

##################################
