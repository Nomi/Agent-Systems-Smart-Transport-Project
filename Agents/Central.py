##General Imports
import random
import os
import sys
import spade
import time
import datetime
import asyncio
import traceback



##Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init

##Importing our functions
from helper import printArrMap



## Global Variables:
ARRMAP_HEIGHT = 20 #try to have this be odd
ARRMAP_WIDTH = 50

## Agent:
class CentralAgent(Agent): #responsible for routing and graphing?
    # routes={}
    # routes['nomanspadehw@01337.io/69']=[1201,1021,2130]
    routeIdxs = range(0,10,1)
    timeOfStart=time.time()
    passengerIDs=[]
    busIDs=[]
    busPositions = {} #hashmap from XMPP IDs to busses' route index.
    arrMap=[]

    # class MyBehav(CyclicBehaviour):
    #     async def on_start(self):
    #         for(busIDs)
    #     async def run(self):
    #         print("Counter: {}".format(self.counter))
    #         self.counter += 1
    #         await asyncio.sleep(1)

    async def setup(self):
        print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        self.arrMap=[]
        for i in range(0,ARRMAP_HEIGHT):
            self.arrMap.append([])
            for j in range(0, ARRMAP_WIDTH):
                if(i%2 != 0):
                    self.arrMap[i][j] = ' '
                else:
                    self.arrMap[i][j] = '='
        printArrMap(self.arrMap)
        return 0
        
    def fillDetails(self, _passengersXMPP: list, _bussesXMPP: list): #Actually, just make each of these message central agent "BUS:busname:starpost(always 0 ?)" for busses and for passengers "P:GETROUTE"/"P:startroute:endroute" for passengers???
        self.passengerIDs = _passengersXMPP
        self.busIDs = _bussesXMPP
    



