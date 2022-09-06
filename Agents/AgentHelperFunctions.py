#General Imports
import random
import os
import sys
import spade
import time
import datetime
import asyncio
import traceback



#Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init




## Helper functions:
from matplotlib import widgets


def printArrMap(arrMap:list):
    strArrMap=""
    for i in range(0,arrMap.__len__()):
        for j in range(0,arrMap[i].__len__()):
            strArrMap+=arrMap[i][j]
        strArrMap+='\n'
    print(strArrMap)

def printArrMapWithBounds(arrMap:list):
    strArrMap="["
    for j in range(0, arrMap[0].__len__()):
        strArrMap+='-'
    strArrMap+=']\n'

    for i in range(0,arrMap.__len__()):
        strArrMap+='['
        for j in range(0,arrMap[i].__len__()):
            strArrMap+=arrMap[i][j]
        strArrMap+=']\n'

    strArrMap+="["
    for j in range(0, arrMap[0].__len__()):
        strArrMap+='-'
    strArrMap+=']\n'
    print(strArrMap)

def printArrMap_OneByOne(arrMap:list):
    for i in range(0,arrMap.__len__()):
        for j in range(0,arrMap[i].__len__()):
            print(arrMap[i][j], end='')
        print()

def buildArrMap(height:int, width:int) -> list:
    arrMap=[]
    for i in range(0,height):
        arrMap.append([])
        for j in range(0, width):
            if((i+1)%3 != 0):
                arrMap[i].append(' ')
            else:
                arrMap[i].append('=')
    return arrMap