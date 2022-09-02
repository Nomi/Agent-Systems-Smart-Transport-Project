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



## Global Variables:


## Agent:
class CentralAgent(Agent): #responsible for routing and graphing?
    # routes={}
    # routes['nomanspadehw@01337.io/69']=[1201,1021,2130]
    routeIdxs = range(0,10,1)
    timeOfStart=time.time()
    passengerIDs=[]
    busIDs=[]
    busPositions = {} #hashmap from XMPP IDs to busses' route index.

    # class MyBehav(CyclicBehaviour):
    #     async def on_start(self):
    #         for(busIDs)
    #     async def run(self):
    #         print("Counter: {}".format(self.counter))
    #         self.counter += 1
    #         await asyncio.sleep(1)

    async def setup(self):
        print(Fore.LIGHTRED_EX + f"Bus Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        return 0
        
    def fillDetails(self, _passengersXMPP: list, _bussesXMPP: list): #Actually, just make each of these message central agent "BUS:busname:starpost(always 0 ?)" for busses and for passengers "P:GETROUTE"/"P:startroute:endroute" for passengers???
        self.passengerIDs = _passengersXMPP
        self.busIDs = _bussesXMPP
    



