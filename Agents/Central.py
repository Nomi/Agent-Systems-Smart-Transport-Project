##General Imports
from http.client import ACCEPTED
import random
import os
from re import X
import sys
from typing import Any
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
from Agents.AgentHelperFunctions import printArrMap, buildArrMap, printArrMapWithBounds, busData, passengerData
from helper import coordinates


## Global Variables:
from config import ARRMAP_HEIGHT, ARRMAP_WIDTH

## Central Agent class:
class CentralAgent(Agent): #responsible for routing and graphing?
    timeOfStart=time.time()
    passengers = dict({}) #hashmap from XMPP JIDs to passengerData
    busses = dict({}) #hashmap from XMPP JIDs to busData
    arrMap=[]

    class myBehavior(CyclicBehaviour):
        async def  on_start(self) -> None:
            print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : READY" + Fore.RESET)
            return await super().on_start()
        async def run(self):
            try:
                msg = await self.receive()
                if msg:
                    # print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : RECIEVED MESSAGE" + Fore.RESET)

                    body = msg.body.split(':')
                    # print(body)
                    if(body[0]=='P'):
                        if(body[1]=='LOOKING_FOR_BUS'):
                            isAccepted:bool = True
                            # print(self.agent.passengers.keys())
                            h = int(body[3]) #y
                            w = int(body[4]) #x
                            timeLimit = int(body[2])
                            self.agent.arrMap[h][w] = 'P'

                            assignedBus = self.agent.assginBusToPassenger(h,w,timeLimit)
                            if(assignedBus == self.agent.jid):
                                isAccepted = False
                                self.agent.arrMap[h][w] = Fore.RED + 'P' + Fore.RESET

                            reply = Message(to=str(msg.sender))
                            if(isAccepted):
                                self.agent.busses[assignedBus].busyPickingPassenger = True
                                if msg._sender not in self.agent.passengers.keys():
                                    self.agent.passengers[msg._sender] = passengerData(coordinates(w,h),assignedBusXmpp=assignedBus)
                                reply.body="--[ACCEPT]--"
                            else:
                                reply.body="--[REJECT]--"
                            await self.send(reply)
                            printArrMapWithBounds(self.agent.arrMap)
                        elif(body[1]=='GOT_ON_BUS'):
                            currPassenger:passengerData = self.agent.passengers[msg.sender]
                            self.agent.busses[currPassenger.assignedBusXmpp].busyPickingPassenger=False
                            self.agent.arrMap[currPassenger.pos.y][currPassenger.pos.x] = ' '
                            self.agent.busses[currPassenger.assignedBusXmpp].passengerCount += 1 #Note: this is just to prevent more than max passengers on bus because if we don't update it here, the count won't update until the next message from the bus itself, before which a passenger may be assigned to it (as such tricking the passenger count check)
                            # print(Fore.BLUE + "lol here"+ Fore.RESET)
                        elif body[1] == "FINISHED":
                            # print(Fore.RED+"DEBUG Central: Passenger finished"+Fore.RESET)
                            dict.pop(self.agent.passengers,msg.sender)
                            # print(self.agent.passengers)

                    elif(body[0]=='B'):
                        #The following is done in the passenger part when they reply they're here. #to--do: set self.agent.buss[assignedBus].busyPickingPassenger to False when current passenger is picked up
                        if(body[1]=="MOVING"):
                            moveRejectedStr = "NOT_REJECT_MOVE"
                            passengerFoundStr = "NOT_FOUND_PASSENGER"
                            pWX = -1
                            pHY = -1
                            passXmpp = ""

                            nH = int(body[2]) #y
                            nW = int(body[3]) #x
                            newSymbol = str(body[4])
                            if msg._sender not in self.agent.busses.keys():
                                self.agent.busses[msg._sender] = busData(coordinates(nW,nH),int(body[5]),int(body[6]))
                            else:
                                w = self.agent.busses[msg._sender].pos.x
                                h = self.agent.busses[msg._sender].pos.y
                                self.agent.arrMap[h][w] = '='
                                self.agent.busses[msg._sender].pos.x = nW
                                self.agent.busses[msg._sender].pos.y = nH
                            if(self.agent.arrMap[nH][nW] != '='): #avoids overlapping busses
                                nW -= 1
                                self.agent.busses[msg._sender].pos.x = nW #have busses spawn at least two to three spaces apart pls :'(
                                moveRejectedStr = "REJECT_MOVE"
                            currBus:busData = self.agent.busses[msg._sender]
                            
                            # if(self.agent.busses[msg._sender].busyPickingPassenger == False): #accept only one passenger at a time to honor timelimits (and make things easier for myself :'))
                            assignedPassJidXmpp:passengerData = self.agent.getCurrentAssignedPassenger(msg.sender)
                            if(assignedPassJidXmpp != None):
                                passengerFoundStr = "PASSENGER_FOUND"
                                passXmpp = str(assignedPassJidXmpp)
                                pasDat: passengerData = self.agent.passengers[assignedPassJidXmpp]
                                pHY = pasDat.pos.y
                                pWX = pasDat.pos.x

                            busReply = Message(to=str(msg.sender))
                            busReply.body = "CEN"+":" + moveRejectedStr +":"+ passengerFoundStr  + ":"+ str(pHY) + ":" + str(pWX)+ ":" + passXmpp
                            await self.send(busReply) #decided to await anyway # no need for await, clearly.

                            #DEPRECATED: bus arrMap overlap logic needs to be handled here:
                            self.agent.arrMap[nH][nW] = newSymbol #reply with current map?
                            printArrMapWithBounds(self.agent.arrMap)
                        elif(body[1]=="FULL_BUS"):
                            moveRejectedStr = "NOT_REJECT_MOVE"
                            passengerFoundStr = "NOT_FOUND_PASSENGER"
                            pWX = -1
                            pHY = -1
                            passXmpp = ""
                            nH = int(body[2]) #y
                            nW = int(body[3]) #x
                            newSymbol = str(body[4])
                            if msg._sender not in self.agent.busses.keys():
                                self.agent.busses[msg._sender] = busData(coordinates(nW,nH),int(body[5]),int(body[6]))
                            else:
                                w = self.agent.busses[msg._sender].pos.x
                                h = self.agent.busses[msg._sender].pos.y
                                self.agent.arrMap[h][w] = '='
                                self.agent.busses[msg._sender].pos.x = nW
                                self.agent.busses[msg._sender].pos.y = nH
                            if(self.agent.arrMap[nH][nW] != '='): #avoids overlapping busses
                                nW -= 1
                                self.agent.busses[msg._sender].pos.x = nW #have busses spawn at least two to three spaces apart pls :'(
                                moveRejectedStr = "REJECT_MOVE"

                            busReply = Message(to=str(msg.sender))
                            busReply.body = "CEN"+":" + moveRejectedStr +":"+ passengerFoundStr  + ":"+ str(pHY) + ":" + str(pWX)+ ":" + passXmpp
                            await self.send(busReply) #decided to await anyway # no need for await, clearly.

                            #DEPRECATED: bus arrMap overlap logic needs to be handled here:
                            self.agent.arrMap[nH][nW] = newSymbol #reply with current map?
                            printArrMapWithBounds(self.agent.arrMap)
                        elif body[1] == "FINISHED":
                            # print(Fore.RED+"DEBUG Central: Bus finished"+Fore.RESET)
                            currBus = self.agent.busses[msg.sender]
                            nW=currBus.pos.x
                            nH=currBus.pos.y
                            currBus=None
                            self.agent.arrMap[nH][nW]="="
                            dict.pop(self.agent.busses,msg.sender)
                            # print(self.agent.busses)
                            printArrMapWithBounds(self.agent.arrMap)
                    else:
                        print("CENTRAL AGENT: Invalid message body.")
            except:
                traceback.print_exc()

    async def setup(self):
        print(Fore.LIGHTYELLOW_EX + f"Central Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)

        behav = self.myBehavior()
        self.add_behaviour(behav)

        self.timeOfStart=time.time()
        self.arrMap=buildArrMap(ARRMAP_HEIGHT,ARRMAP_WIDTH)
        random.seed(time.time_ns())
        # for i in range(0,6,1):
        #     pos = self.getRandomPassengerLocation(self.arrMap)
        #     x=pos["x"]
        #     y=pos["y"]
        #     self.arrMap[y][x]="P"

        printArrMapWithBounds(self.arrMap)
        return 0
        
    def fillDetails(self, _passengersXMPP: list, _bussesXMPP: list): #Actually, just make each of these message central agent "BUS:busname:starpost(always 0 ?)" for busses and for passengers "P:GETROUTE"/"P:startroute:endroute" for passengers???
        # self.passengerIDs = _passengersXMPP
        # self.busIDs = _bussesXMPP
        print("Central agent fillDetails not implemented or needed?")

    def getRandomPassengerLocation(self) -> dict:
        positionNotFound = True
        maxX = self.arrMap[0].__len__()-2 #never on the last block
        maxY = self.arrMap.__len__()-1
        x=0
        y=0
        while(positionNotFound):
            x = random.randint(0,maxX)
            y = random.randint(0,maxY)
            if(self.arrMap[y][x]=='='):
                if(self.arrMap[y+1][x]==' '):
                    y=y+1
                else:
                    y=y-1
            if(self.arrMap[y][x]==' ' and (self.arrMap[y-1][x]=='=' or self.arrMap[y+1][x]=='=')):
                positionNotFound = False
                self.arrMap[y][x] = 'R' #Reserved for passenger.
        return dict({"x":x, "y": y})

    def assginBusToPassenger(self, hY:int, wX:int, timeLimit:int) -> Any:
        nearestBusXmpp = self.jid
        nearestBusDistance = -1
        for k in self.busses.keys():
            bus:busData = self.busses[k] 
            # print(Fore.RED +"lol"+str(wX-bus.pos.x))
            #TODO: the last condition for length might need a multiplier of distance in = with number of seconds per = sign from config file
            if ((not bus.busyPickingPassenger) and (bus.passengerCount != bus.maxPassengers) and (bus.pos.y+1 == hY or bus.pos.y-1 == hY) and ((wX - bus.pos.x) > 1) and ((wX - bus.pos.x) < timeLimit-1)): #timeLimit-1 just for extra breathing room.
                # print(str(wX-bus.pos.x))
                if((wX-bus.pos.x)<nearestBusDistance or nearestBusDistance == -1):
                    nearestBusXmpp = k
                    nearestBusDistance = wX-bus.pos.x
        return nearestBusXmpp

    def getCurrentAssignedPassenger(self, busJidXmpp) -> Any:
        for passengerJid in self.passengers:
            passenger:passengerData = self.passengers[passengerJid]
            if(passenger.assignedBusXmpp == busJidXmpp):
                return passengerJid
        return None