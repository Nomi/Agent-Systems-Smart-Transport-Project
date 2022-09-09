###General Imports
from email import message
from pickle import TRUE
from queue import Full
import random
import os
import sys
from threading import Timer
from timeit import timeit
from tkinter import LAST
from unicodedata import numeric
import spade
import time
import datetime
import asyncio
import traceback
import string



###Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init
from Agents.AgentHelperFunctions import passengerData
from Agents.Passenger import FINISHED

### Importing our code
from helper import coordinates

### Global Variables
from config import MAX_PASSENGERS, LAST_STOP, SYMBOL_FULLBUSS, SYMBOL_NOTFULLBUSS, TIME2SLEEP4



## States:
MOVING = "MOVING"
PICKING_UP_CLIENT = "PICKING_UP_CLIENT" #Do not disturb
DROPPING_OFF_CLIENT = "DROPPING_OFF_CLIENT" #Do not disturb when near destination of passenger.
FULL_BUSS = "FULL_BUSS" #Do not disturb
FINAL_STOP = "FINAL_STOP"

class BusAgent(Agent):
    route=[]
    #finalStopIndex = -1 #use (route.__len__()-1) instead
    colorId=Fore.RED#change to be filled from fillDetails
    currentPos = coordinates(0,0)
    centralAgentAddress=""
    passengerCount=0
    passengersToPick = dict({})
    timeOfStart=time.time()
    lastXPos = LAST_STOP

    async def setup(self):
        self.add_behaviour(TransitFiniteStates())
        print(Fore.LIGHTRED_EX + f"Bus Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        return 0
        
    def fillDetails(self, CentralAgentXMPPID: string, hY:int, wX:int):
        self.centralAgentAddress=CentralAgentXMPPID
        self.currentPos=coordinates(wX,hY)
        # self.currentStopIndex=0

class TransitFiniteStates(FSMBehaviour):
    async def on_start(self):
        self.add_state(name=MOVING, state=Moving_StateBehavior(),initial=True)
        self.add_state(name=PICKING_UP_CLIENT, state=PickingUpCient_StateBehavior())
        # # self.add_state(name=DROPPING_OFF_CLIENT, state=RidingBus_StateBehavior()) #probably can remove getting off from passenger's agent
        self.add_state(name=FULL_BUSS, state=FullBus_StateBehavior())
        self.add_state(name=FINAL_STOP, state=FinalStop_StateBehavior())
        

        # # self.add_transition(source=MOVING, dest=DROPPING_OFF_CLIENT)
        # self.add_transition(source=PICKING_UP_CLIENT, dest=MOVING)

        # # self.add_transition(source=FULL_BUSS, dest=DROPPING_OFF_CLIENT)
        # # self.add_transition(source=DROPPING_OFF_CLIENT, dest=AT_BUS_STOP)


        self.add_transition(source=MOVING, dest=MOVING)
        self.add_transition(source=MOVING, dest=PICKING_UP_CLIENT)
        # self.add_transition(source=PICKING_UP_CLIENT, dest=PICKING_UP_CLIENT)
        self.add_transition(source=PICKING_UP_CLIENT, dest=MOVING)
        self.add_transition(source=PICKING_UP_CLIENT, dest=FULL_BUSS)
        ## self.add_transition(source=DROPPING_OFF_CLIENT, dest=DROPPING_OFF_CLIENT)
        self.add_transition(source=FULL_BUSS, dest=FULL_BUSS)        
        self.add_transition(source=MOVING, dest=FINAL_STOP)
        self.add_transition(source=FULL_BUSS, dest=FINAL_STOP)
        # self.add_transition(source=FINAL_STOP, dest=FINAL_STOP)
        # # self.add_transition(source=AT_BUS_STOP, dest=AT_BUS_STOP)

# class AtBusStop_StateBehavior(State): #FIN
#     async def run(self):

#         print("DEBUG: Checking if we're assigned passengers (10 secs).")
#         try:
#             msg = await self.receive(timeout=10)
#             if msg: #should contain the graph position of the passenger's position somehow
#                 message = msg.body.split(':')
#                 baserouteidx = message[0]
#                 detourrouteidx = message[1]
#                 self.agent.route.

#             searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
#             print(searchTimeSoFar)
#             if(searchTimeSoFar >= self.agent.timelimit):
#                 #NOTIFY CENTRAL AGENT TO CANCEL??
#                 self.set_next_state(FINISHED)
#             else:
#                 self.set_next_state(LOOKING_FOR_RIDE)
#                 await asyncio.sleep(2)
#         except:
#             traceback.print_exc()

class Moving_StateBehavior(State): #FIN
    async def run(self):
        print(f"DEBUG: bus agent {str(self.agent.jid)} on the move.")
        try:
            stateChangeFromMoving:bool = False
            #implement passenger pickup logic
            if self.agent.currentPos.x != self.agent.lastXPos:
                # move by one index (width):
                self.agent.currentPos.x = 1 + self.agent.currentPos.x #wait for another bus to move so that there's no overlap?
                x = self.agent.currentPos.x
                y = self.agent.currentPos.y
                # send location info to Central agent
                msg = Message(to=self.agent.centralAgentAddress)
                pasCountWithSymbol = f"{self.agent.passengerCount}"
                if self.agent.passengerCount == MAX_PASSENGERS:
                    pasCountWithSymbol += SYMBOL_FULLBUSS
                else:
                    pasCountWithSymbol += SYMBOL_NOTFULLBUSS
                msg.body = f"B:MOVING:{y}:{x}:{pasCountWithSymbol}:{self.agent.passengerCount}:{MAX_PASSENGERS}" #make this work with dynamically, for now I have it static for testing.
                await self.send(msg)

                # Get message from Central agent (and wait for 1 second to maintain speed of 1 index per second)
                timeBeforeWaitNS = time.time_ns()
                reply = await self.receive(timeout=TIME2SLEEP4)
                if reply:
                    body = reply.body.split(':')
                    print(Fore.RED + "DEBUG: Bus recieved reply with body:")
                    print(body)
                    print(Fore.RESET)
                    if body[1] == "REJECT_MOVE":
                        self.agent.currentPos.x -= 1
                    #else movement accepted.
                    if body[2] == "PASSENGER_FOUND":
                        py=int(body[3])
                        px=int(body[4])
                        passXmpp = str(body[5])
                        self.agent.passengersToPick[passXmpp] = coordinates(px, py)
                print(Fore.RED+ "BUS DEBUG: " + Fore.RESET)
                print(self.agent.passengersToPick.keys())
                #check if passengers are needed to be picked at the current stop. #change to pick only one passenger at a time to commit to a promised timelimit?
                for key in self.agent.passengersToPick.keys():
                    #don't need to check y coordinate here, do I?
                    if((self.agent.passengersToPick[key].y-1 == self.agent.currentPos.y) or (self.agent.passengersToPick[key].y+1 == self.agent.currentPos.y)):
                        print(Fore.RED+ "BUS DEBUG: HERE!!! " + Fore.RESET)
                        if(self.agent.passengersToPick[key].x == self.agent.currentPos.x):
                            print(Fore.RED+ "BUS DEBUG: !here! " + Fore.RESET)
                            stateChangeFromMoving = True
                            self.set_next_state(PICKING_UP_CLIENT)

                if(not stateChangeFromMoving):
                    self.set_next_state(MOVING) 
                    timeRemainingSeconds = TIME2SLEEP4 - (time.time_ns() - timeBeforeWaitNS)/1000000000
                    if timeRemainingSeconds > 0:
                        await asyncio.sleep(timeRemainingSeconds) #we move one array index per second. #replace with recieve message with timeout of 1 sec and after this, sleep for the part of 1 sec that wasn't waited for.
                #implement accept or reject replies so that you can have the central agent check if there's any busses ahead of you currently?
                #though tbh, we probably won't need that because every bus spawns at different locations and each of them have the same speed and no stops until the end
            else:
                self.set_next_state(FINAL_STOP)
        except:
            traceback.print_exc()

class PickingUpCient_StateBehavior(State):
    async def run(self):
        try:
            #Notify the passenger that: "YOU HAVE BEEN PICKED!" (no threatening pls)
            print(Fore.RED+ "BUS: Picking up client not implemented" + Fore.RESET)
            for passJID in self.agent.passengersToPick.keys():
                currPassenger:coordinates = self.agent.passengersToPick[passJID]
                if(currPassenger.x == self.agent.currentPos.x):
                    msg = Message(to = str(passJID))
                    msg.body = "--[BUS_HERE]--"
                    self.agent.passengerCount+=1
                    await self.send(msg)

            #TODO(maybe?): Message the central agent the passenger with given id was picked up 
            #?should i or should i not?
            
            # Go back to moving or full buss state
            if(self.agent.passengerCount == MAX_PASSENGERS):
                print("DEBUG bus: picking client -> fullbus not implemented")
            else:
                self.set_next_state(MOVING)
            await asyncio.sleep(TIME2SLEEP4)
        except:
            traceback.print_exc()

class FullBus_StateBehavior(State):
    async def run(self):
        print(f"DEBUG: bus agent {str(self.agent.jid)} is FULLY OCCUPIED and moving.")
        try:
            stateChangeFromMoving:bool = False
            if self.agent.currentPos.x != self.agent.lastXPos:
                # move by one index (width):
                self.agent.currentPos.x = 1 + self.agent.currentPos.x #wait for another bus to move so that there's no overlap?
                x = self.agent.currentPos.x
                y = self.agent.currentPos.y
                # send location info to Central agent
                msg = Message(to=self.agent.centralAgentAddress)
                pasCountWithSymbol = f"{self.agent.passengerCount}"
                pasCountWithSymbol += SYMBOL_FULLBUSS
                msg.body = f"B:FULL_BUS:{y}:{x}:{pasCountWithSymbol}:{self.agent.passengerCount}:{MAX_PASSENGERS}" #make this work with dynamically, for now I have it static for testing.
                await self.send(msg)

                # Get message from Central agent (and wait for required number of seconds)
                timeBeforeWaitNS = time.time_ns()
                reply = await self.receive(timeout=TIME2SLEEP4)
                if reply:
                    body = reply.body.split(':')
                    print(Fore.RED + "DEBUG: Bus (FULL_BUS) recieved reply with body:")
                    print(body)
                    print(Fore.RESET)
                    if body[1] == "REJECT_MOVE":
                        self.agent.currentPos.x -= 1
                    #else movement accepted.
                
                self.set_next_state(FULL_BUSS) 
                timeRemainingSeconds = TIME2SLEEP4 - (time.time_ns() - timeBeforeWaitNS)/1000000000
                if timeRemainingSeconds > 0:
                    await asyncio.sleep(timeRemainingSeconds)
            else:
                self.set_next_state(FINAL_STOP)
        except:
            traceback.print_exc()

class FinalStop_StateBehavior(State):
    async def run(self):
        try:
            print(Fore.RED + f"Bus Agent {self.get('id')} : FINISHED JOURNEY  [jid: {str(self.agent.jid)}]" + Fore.RESET)
            print("DEBUG bus: FinalStop behavior not implemented yet.")
            #Notify passengers we are at final stop (TODO: from passengers notify Central agent of them finishing and from central handle those messages)
            for passJid in self.agent.passengersToPick.keys():
                tmpMsg = Message(to=passJid)
                tmpMsg.body = "--[REACHED_DESTINATION]--"
                await self.send(tmpMsg)
            #Notify central agent you are finished.
            farewellMsg = Message(to= self.agent.centralAgentAddress)
            farewellMsg.body = "B:"+"FINISHED"
            await self.send(farewellMsg)
            #TODO: From central agent delete all entries in the hashtable belonging to finished bus and it's passengers.
        except:
            traceback.print_exc()