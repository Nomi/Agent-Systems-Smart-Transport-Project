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
from Agents.Passenger import FINISHED_STATE

### Importing our code
from helper import coordinates

### Global Variables
from config import MAX_PASSENGERS, LAST_STOP, SYMBOL_FULLBUSS, SYMBOL_NOTFULLBUSS, TIME2SLEEP4, SECOND2NANOSECOND
## States:
MOVING_STATE = "MOVING"
PICKING_UP_CLIENT_STATE = "PICKING_UP_CLIENT" #Do not disturb
DROPPING_OFF_CLIENT_STATE = "DROPPING_OFF_CLIENT" #Do not disturb when near destination of passenger.
FULL_BUSS_STATE = "FULL_BUSS" #Do not disturb
FINAL_STOP_STATE = "FINAL_STOP"


class BusAgent(Agent):
    route=[]
    # colorId=Fore.RED#change to be filled from fillDetails
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
        self.add_state(name=MOVING_STATE, state=Moving_StateBehavior(),initial=True)
        self.add_state(name=PICKING_UP_CLIENT_STATE, state=PickingUpCient_StateBehavior())
        # # self.add_state(name=DROPPING_OFF_CLIENT, state=RidingBus_StateBehavior()) #probably can remove getting off from passenger's agent
        self.add_state(name=FULL_BUSS_STATE, state=FullBus_StateBehavior())
        self.add_state(name=FINAL_STOP_STATE, state=FinalStop_StateBehavior())
        

        # # self.add_transition(source=MOVING, dest=DROPPING_OFF_CLIENT)
        # self.add_transition(source=PICKING_UP_CLIENT, dest=MOVING)

        # # self.add_transition(source=FULL_BUSS, dest=DROPPING_OFF_CLIENT)
        # # self.add_transition(source=DROPPING_OFF_CLIENT, dest=AT_BUS_STOP)


        self.add_transition(source=MOVING_STATE, dest=MOVING_STATE)
        self.add_transition(source=MOVING_STATE, dest=PICKING_UP_CLIENT_STATE)
        # self.add_transition(source=PICKING_UP_CLIENT, dest=PICKING_UP_CLIENT)
        self.add_transition(source=PICKING_UP_CLIENT_STATE, dest=MOVING_STATE)
        self.add_transition(source=PICKING_UP_CLIENT_STATE, dest=FULL_BUSS_STATE)
        ## self.add_transition(source=DROPPING_OFF_CLIENT, dest=DROPPING_OFF_CLIENT)
        self.add_transition(source=FULL_BUSS_STATE, dest=FULL_BUSS_STATE)        
        self.add_transition(source=MOVING_STATE, dest=FINAL_STOP_STATE)
        self.add_transition(source=FULL_BUSS_STATE, dest=FINAL_STOP_STATE)
        # self.add_transition(source=FINAL_STOP, dest=FINAL_STOP)
        # # self.add_transition(source=AT_BUS_STOP, dest=AT_BUS_STOP)

class Moving_StateBehavior(State): #FIN
    async def run(self):
        # print(f"DEBUG: bus agent {str(self.agent.jid)} on the move.")
        try:
            stateChangeFromMoving:bool = False
            if self.agent.currentPos.x != self.agent.lastXPos:
                # move by one index (width):
                self.agent.currentPos.x = 1 + self.agent.currentPos.x 
                x = self.agent.currentPos.x
                y = self.agent.currentPos.y
                # send location info to Central agent
                msg = Message(to=self.agent.centralAgentAddress)
                pasCountWithSymbol = f"{self.agent.passengerCount}"
                if self.agent.passengerCount == MAX_PASSENGERS:
                    pasCountWithSymbol += SYMBOL_FULLBUSS
                else:
                    pasCountWithSymbol += SYMBOL_NOTFULLBUSS
                msg.body = f"B:MOVING:{y}:{x}:{pasCountWithSymbol}:{self.agent.passengerCount}:{MAX_PASSENGERS}"
                await self.send(msg)

                # Get message from Central agent (and wait for required number of seconds as per the config (maintains speed))
                timeBeforeWaitNS = time.time_ns()
                reply = await self.receive(timeout=TIME2SLEEP4)
                if reply:
                    body = reply.body.split(':')
                    # print(Fore.RED + "DEBUG: Bus recieved reply with body:")
                    # print(body)
                    # print(Fore.RESET)
                    if body[1] == "REJECT_MOVE":
                        self.agent.currentPos.x -= 1
                    #else movement accepted.
                    if body[2] == "PASSENGER_FOUND":
                        py=int(body[3])
                        px=int(body[4])
                        passXmpp = str(body[5])
                        self.agent.passengersToPick[passXmpp] = coordinates(px, py)
                # print(Fore.RED+ "BUS DEBUG: " + Fore.RESET)
                # print(self.agent.passengersToPick.keys())

                #check if passengers are needed to be picked at the current stop. #change to pick only one passenger at a time to commit to a promised timelimit?
                for key in self.agent.passengersToPick.keys():
                    if(self.agent.passengersToPick[key].x == self.agent.currentPos.x):
                        # print(Fore.RED+ "BUS DEBUG: !here! " + Fore.RESET)
                        stateChangeFromMoving = True
                        self.set_next_state(PICKING_UP_CLIENT_STATE)

                if(not stateChangeFromMoving):
                    self.set_next_state(MOVING_STATE) 
                    timeRemainingSeconds = TIME2SLEEP4 - (time.time_ns() - timeBeforeWaitNS)/1000000000
                    if timeRemainingSeconds > 0:
                        await asyncio.sleep(timeRemainingSeconds)
            else:
                self.set_next_state(FINAL_STOP_STATE)
        except:
            traceback.print_exc()

class PickingUpCient_StateBehavior(State):
    async def run(self):
        try:
            #Notify the passenger that: "YOU HAVE BEEN PICKED!" (no threats pls :P)
            for passJID in self.agent.passengersToPick.keys():
                currPassenger:coordinates = self.agent.passengersToPick[passJID]
                if(currPassenger.x == self.agent.currentPos.x):
                    msg = Message(to = str(passJID))
                    msg.body = "--[BUS_HERE]--"
                    self.agent.passengerCount+=1
                    await self.send(msg)
            
            # Go back to moving or full buss state as appropriate.
            if(self.agent.passengerCount == MAX_PASSENGERS):
                self.set_next_state(FULL_BUSS_STATE)
            else:
                self.set_next_state(MOVING_STATE)
            await asyncio.sleep(TIME2SLEEP4)
        except:
            traceback.print_exc()

class FullBus_StateBehavior(State):
    async def run(self):
        # print(f"DEBUG: bus agent {str(self.agent.jid)} is FULLY OCCUPIED and moving.")
        try:
            stateChangeFromMoving:bool = False
            if self.agent.currentPos.x != self.agent.lastXPos:
                # move by one index (width):
                self.agent.currentPos.x = 1 + self.agent.currentPos.x 
                x = self.agent.currentPos.x
                y = self.agent.currentPos.y
                # send location info to Central agent
                msg = Message(to=self.agent.centralAgentAddress)
                pasCountWithSymbol = f"{self.agent.passengerCount}"
                pasCountWithSymbol += SYMBOL_FULLBUSS
                msg.body = f"B:FULL_BUS:{y}:{x}:{pasCountWithSymbol}:{self.agent.passengerCount}:{MAX_PASSENGERS}"
                await self.send(msg)

                # Get message from Central agent (and wait for required number of seconds)
                timeBeforeWaitNS = time.time_ns()
                reply = await self.receive(timeout=TIME2SLEEP4)
                if reply:
                    body = reply.body.split(':')
                    if body[1] == "REJECT_MOVE":
                        self.agent.currentPos.x -= 1
                    #else movement accepted.
                
                self.set_next_state(FULL_BUSS_STATE) 
                timeRemainingSeconds = TIME2SLEEP4 - (time.time_ns() - timeBeforeWaitNS)/SECOND2NANOSECOND
                if timeRemainingSeconds > 0:
                    await asyncio.sleep(timeRemainingSeconds)
            else:
                self.set_next_state(FINAL_STOP_STATE)
        except:
            traceback.print_exc()

class FinalStop_StateBehavior(State):
    async def run(self):
        try:
            print(Fore.RED + f"Bus Agent {self.get('id')} : FINISHED JOURNEY  [jid: {str(self.agent.jid)}]" + Fore.RESET)
            # print("DEBUG bus: FinalStop behavior not implemented yet.")

            #Notify passengers we are at final stop
            for passJid in self.agent.passengersToPick.keys():
                tmpMsg = Message(to=passJid)
                tmpMsg.body = "--[REACHED_DESTINATION]--"
                await self.send(tmpMsg)
            #Notify central agent you are finished.
            farewellMsg = Message(to= self.agent.centralAgentAddress)
            farewellMsg.body = "B:"+"FINISHED"
            await self.send(farewellMsg)
        except:
            traceback.print_exc()