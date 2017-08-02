#!/usr/bin python

##This parses a config text file and looks for the arguments you specify in the function configParse. It will update functions that have updateOnRun=True and are numeric (see options section below)

import sys
import os

#to access the n'th argument data use configReturns[n][0] - to see whether it was changed: configReturns[n][1] will be True if it was changed and False if not
#could possibly generalise this function in future to merely be a file parser and manipulate the data somewhere else
class configOption:
    def __init__(self, name = "NULL", **kwargs):
        self.name = name
        self.optionType = "numeric"
        self.updateOnRun = True
        self.variables = kwargs
    def getName(self):
        return self.name
    def setVariable(self, k, v):
        variables[k] = v;
    def getVariable(self, k):
        return self.variables[k]

def configParse(curroPath, *args):
    config = open(curroPath+"/configuration/config.txt", "r")
    argumentValues = [[0, False]] #lists within a list (format: [Option number in order of passing to funciton][VALUE, EXISTS])
    index = 1
    
    configContents = config.read() 
    for argument in args:
        #extracts the current number after config into captureCount
        currentOption = configOption(argument)
        
        #OPTIONS SECTION
        if(currentOption.name in ["HOST","reventPath","targetReventPath","waPath"]):
            currentOption.updateOnRun = False
            currentOption.optionType = "text"
        
        #</ OPTIONS SECTION
        
        #Find line in file and 
        argumentValues.append([0, False])

        config.seek(0)
        for line in config:
            if(line.startswith((str(argument)+ ": "), 0, len(str(line)))):
                argumentValues[index] = ( [(str(line)[len(str(currentOption.name))+2:(len(str(line)))]).strip(), True] )
                break

        if(argumentValues[index][1]==False and currentOption.optionType=="numeric"): #Didn't find the config option so create it automatically
            configContents =  "\n" + configContents + str((argument+": 0"))
        elif(argumentValues[index][1]==False and currentOption.optionType=="text"):
            configContents = "\n" + configContents + str((argument+": "))

        config.seek(0) #Update those config values that need updating
        if(currentOption.updateOnRun==True):
            configContents = configContents.replace((str(argument)+": "+str(int(argumentValues[index][0]))),(str(argument)+": "+str(int(argumentValues[index][0])+1)))
        index = index + 1
            
    os.remove(curroPath+"/configuration/config.txt")
    config.close()
    config = open(curroPath+"/configuration/config.txt", "w")
    config.write(configContents)
    return argumentValues
    
#import ipdb; ipdb.set_trace()
#for debugging ^^
