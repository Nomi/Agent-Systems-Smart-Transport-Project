##General Imports
import random
import os
from re import X
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
from Agents.AgentHelperFunctions import printArrMap, buildArrMap, printArrMapWithBounds
from helper import coordinates


## Global Variables:
from config import ARRMAP_HEIGHT, ARRMAP_WIDTH

## Agent:
class CentralAgent(Agent): #responsible for routing and graphing?
    # routes={}
    # routes['nomanspadehw@01337.io/69']=[1201,1021,2130]
    # routeIdxs = range(0,10,1)
    timeOfStart=time.time()
    passengerIDs=[]
    busPositions = dict({}) #hashmap from XMPP IDs to busses' route index.
    arrMap=[]

    # class MyBehav(CyclicBehaviour):
    #     async def on_start(self):
    #         for(busIDs)
    #     async def run(self):
    #         print("Counter: {}".format(self.counter))
    #         self.counter += 1
    #         await asyncio.sleep(1)
    class myBehavior(CyclicBehaviour):
        async def  on_start(self) -> None:
            print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : READY" + Fore.RESET)
            return await super().on_start()
        async def run(self):
            try:
                msg = await self.receive()
                if msg:
                    print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : RECIEVED MESSAGE" + Fore.RESET)

                    body = msg.body.split(':')
                    print(body)
                    if(body[0]=='P'):
                        self.agent.passengerIDs.append(msg._sender)
                        print(self.agent.passengerIDs[self.agent.passengerIDs.__len__()-1])
                        w = int(body[3]) #x
                        h = int(body[2]) #y
                        self.agent.arrMap[w][h] = 'P'
                        # if(y>=0+2 and y<self.agent.arrMap.__len__()-2):
                        #     if(self.agent.arrMap[y+1][x]):
                        printArrMapWithBounds(self.agent.arrMap)
                        #need to handle the finding nearest bus (that's on the adjacent route) and assigning the passenger to them,
                        #also, if timelimit for pickup is lesser than time it will take to pick up someone, send --[REJECT]--
                    elif(body[0]=='B'):
                        print("Handling messages by bus not enabled yet.")
                        #body[1] reserved for purpose (e.g. picked up, starting, picking up, moving, etc.) #moving also serves as registration
                        nW = int(body[2]) #x
                        nH = int(body[3]) #y
                        newSymbol = str(body[4])
                        if msg._sender not in self.agent.busPositions.keys():
                            self.agent.busPositions[msg._sender] = coordinates(nW,nH)
                        else:
                            w = self.agent.busPositions[msg._sender].x
                            h = self.agent.busPositions[msg._sender].y
                            self.agent.arrMap[h][w] = ' ' #bus arrMap overlap logic also needs to be accounted for here.
                            self.agent.busPositions[msg._sender].x = nW
                            self.agent.busPositions[msg._sender].y = nH
                        #bus arrMap overlap logic needs to be handled here:
                        self.agent.arrMap[nH][nW] = newSymbol
                        #reply with current map?
                        printArrMapWithBounds(self.agent.arrMap)
                    else:
                        print("Invalid message body.")
            except:
                traceback.print_exc()

    async def setup(self):
        print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)

        behav = self.myBehavior()
        self.add_behaviour(behav)

        self.timeOfStart=time.time()
        self.arrMap=buildArrMap(ARRMAP_HEIGHT,ARRMAP_WIDTH)
        random.seed(time.time_ns)
        # for i in range(0,6,1):
        #     pos = self.getRandomPassengerLocation(self.arrMap)
        #     x=pos["x"]
        #     y=pos["y"]
        #     self.arrMap[y][x]="P"

        printArrMapWithBounds(self.arrMap)
        return 0
        
    def fillDetails(self, _passengersXMPP: list, _bussesXMPP: list): #Actually, just make each of these message central agent "BUS:busname:starpost(always 0 ?)" for busses and for passengers "P:GETROUTE"/"P:startroute:endroute" for passengers???
        self.passengerIDs = _passengersXMPP
        self.busIDs = _bussesXMPP

    def getRandomPassengerLocation(self) -> dict:
        positionNotFound = True
        maxX = self.arrMap[0].__len__()-1
        maxY = self.arrMap.__len__()-1
        x=0
        y=0
        while(positionNotFound):
            x = random.randint(0,maxX)
            y = random.randint(0,maxY)
            if(self.arrMap[y][x]=='='):
                y=y+1
            if(self.arrMap[y][x]==' '):
                positionNotFound = False
        return dict({"x":x, "y": y})

    # def getRandomBusLocation(self) -> dict:
    #     positionNotFound = True
    #     maxX = self.arrMap[0].__len__()-1
    #     maxY = self.arrMap.__len__()-1
    #     x=0
    #     y=0
    #     while(positionNotFound):
    #         x = random.randint(0,maxX)
    #         y = random.randint(0,maxY)
    #         if(self.arrMap[y][x]==' '):
    #             y=y+1
    #         if(self.arrMap[y][x]=='='):
    #             positionNotFound = False
    #     return dict({"x":x, "y": y})

