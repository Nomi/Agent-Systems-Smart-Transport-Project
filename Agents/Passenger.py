### General Imports
from asyncio import staggered
from email import message
import random
import os
import string
import sys
from xmlrpc.client import boolean
import spade
import time
import datetime
import asyncio
import traceback



### Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init

from Agents.Central import CentralAgent
from config import ARRMAP_WIDTH
from helper import coordinates
# from Faker import faker()



### Global Variables
# States:
LOOKING_FOR_RIDE_STATE = "LOOKING_FOR_RIDE"
WAITING_FOR_RIDE_STATE = "WAITING_FOR_RIDE"
RIDING_STATE = "RIDING"
GETTING_OFF_STATE= "GETTING_OFF"
FINISHED_STATE="FINISHED"



### Main class:
class PassengerAgent(Agent):
    # destination=""
    # location=""
    centralAgentAddress=""
    timeOfStart=None
    timelimit= int(ARRMAP_WIDTH/2) #1000000 #20 #4 #seconds
    succesfullyCompleted=None
    # currentColor = ""
    currentBusXmppJID = None
    position = None

    async def setup(self):
        self.add_behaviour(TransitFiniteStates())
        print(Fore.CYAN + f"Passenger Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        self.succesfullyCompleted=False
        return 0
        
    def fillDetails(self, CentralAgentXMPPID: string, position:dict, destination:string, test:bool = False):
        self.position = dict({
        "x": -1,
        "y": -1
        })
        self.centralAgentAddress=CentralAgentXMPPID
        self.position=position
        self.destination=destination
        ## For testing:
        if(test):
            self.position["y"]=1
            self.position["x"]=4

    def getCurrentColor(self):
        return self.currentColor


class RequestBus(OneShotBehaviour):
    async def on_start(self):
        self.agent.currentColor = "yellow"
    async def run(self):
        msg = Message(to=str(self.agent.centralAgentAddress))
        msg.body="P:"+"LOOKING_FOR_BUS"+":"+str(self.agent.timelimit)+":"+str(self.agent.position["y"])+":"+str(self.agent.position["x"])
        await self.send(msg)


class TransitFiniteStates(FSMBehaviour):
    async def on_start(self):
        self.add_state(name=LOOKING_FOR_RIDE_STATE, state=LookForBus_StateBehavior(), initial=True)
        self.add_state(name=WAITING_FOR_RIDE_STATE, state=WaitingForBus_StateBehavior())
        self.add_state(name=RIDING_STATE, state=RidingBus_StateBehavior())
        # self.add_state(name=GETTING_OFF, state=GettingOff_StateBehavior())
        self.add_state(name=FINISHED_STATE, state=Finished_StateBehavior())
        self.add_transition(source=LOOKING_FOR_RIDE_STATE, dest=LOOKING_FOR_RIDE_STATE)#
        self.add_transition(source=LOOKING_FOR_RIDE_STATE, dest=WAITING_FOR_RIDE_STATE)#
        self.add_transition(source=WAITING_FOR_RIDE_STATE, dest=WAITING_FOR_RIDE_STATE)
        self.add_transition(source=WAITING_FOR_RIDE_STATE, dest=RIDING_STATE)
        self.add_transition(source=RIDING_STATE, dest=RIDING_STATE)
        # self.add_transition(source=RIDING, dest=GETTING_OFF)
        # self.add_transition(source=GETTING_OFF, dest=FINISHED)
        self.add_transition(source=RIDING_STATE, dest=FINISHED_STATE)
        # self.add_transition(source=FINISHED, dest=FINISHED)
        self.add_transition(source=LOOKING_FOR_RIDE_STATE, dest=FINISHED_STATE)#
        # self.add_transition(source=WAITING_FOR_RIDE, dest=FINISHED)#

class LookForBus_StateBehavior(State): #FIN
    async def on_end(self):
        self.agent.currentColor = "blue"
        
    async def run(self):
        notFoundBus = True
        # print("DEBUG: looking for bus.")
        try:
            msg = await self.receive(timeout=self.agent.timelimit)
            if msg:
                if(msg.body=="--[ACCEPT]--"):
                    # print("debug passenger: ride found")
                    notFoundBus=False
                    self.set_next_state(WAITING_FOR_RIDE_STATE)
                elif(msg.body=="--[REJECT]--"):
                    self.set_next_state(FINISHED_STATE)
                else:
                    print("Passenger looking for bus stage: invalid reply gotten.")
            else:
                searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
                # print(searchTimeSoFar)
                if(notFoundBus):
                    #the following if statement should be unneeded because of the timeout?
                    if(searchTimeSoFar >= self.agent.timelimit):
                        #NOTIFY CENTRAL AGENT TO CANCEL??
                        self.set_next_state(FINISHED_STATE)
                    else:
                        self.set_next_state(LOOKING_FOR_RIDE_STATE)
                        await asyncio.sleep(2)
                    
        except:
            traceback.print_exc()

class WaitingForBus_StateBehavior(State):
    async def run(self):
        try:
            changedState:bool = False
            msg = await self.receive()
            if msg:
                if(msg.body=="--[BUS_HERE]--"):
                    selfagent:PassengerAgent = self.agent
                    selfagent.currentBusXmppJID=msg.sender
                    notifyCenMsg = Message(to= str(selfagent.centralAgentAddress))
                    notifyCenMsg.body="P:"+"GOT_ON_BUS"
                    changedState = True
                    await self.send(notifyCenMsg)
                    self.set_next_state(RIDING_STATE)

            # searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
            # if(searchTimeSoFar >= self.agent.timelimit):
            #     #NOTIFY CENTRAL AGENT TO CANCEL??
            #     changedState = True
            #     self.set_next_state(FINISHED)

            if not changedState:
                self.set_next_state(WAITING_FOR_RIDE_STATE)
                await asyncio.sleep(2)
        except:
            traceback.print_exc()

class RidingBus_StateBehavior(State):
    async def run(self):
        try:
            msg = await self.receive()
            if msg:
                if(msg.body=="--[REACHED_DESTINATION]--"):
                    # self.set_next_state(GETTING_OFF)
                    # print("DEBUG passenger: Recieved \"--[REACHED_DESTINATION]--\"")
                    self.set_next_state(FINISHED_STATE)
                    return
            self.set_next_state(RIDING_STATE)
            # await asyncio.sleep(2)
        except:
            traceback.print_exc()
    async def on_end(self) -> None:
        self.agent.succesfullyCompleted=True#now that getting off is not a state, this needs to be here.
        return await super().on_end()

# class GettingOff_StateBehavior(State):
#     async def run(self):
#         try:
#             self.agent.succesfullyCompleted=True
#             ##Send message you've gotten off
#             self.set_next_state(FINISHED)
#             await asyncio.sleep(2)
#         except:
#             traceback.print_exc()

class Finished_StateBehavior(State):
    async def run(self):
        try:
            if(self.agent.succesfullyCompleted):
                print(Fore.CYAN + f"Passenger Agent {self.get('id')} : FINISHED MY JOURNEY     [jid: {str(self.agent.jid)}]" + Fore.RESET)
                msg = Message(to= self.agent.centralAgentAddress)
                msg.body = "P:"+"FINISHED"
                await self.send(msg)
            else:
                print(Fore.CYAN + f"Passenger Agent {self.get('id')} : FAILED TO TRAVEL     [jid: {str(self.agent.jid)}]" + Fore.RESET)
                ## don't need the following anymore because central agent takes care of timelimits.
                # msg = Message(to=self.agent.centralAgentAddress)
                # msg.body='P:'+'--[CANCEL]--'
        except:
            traceback.print_exc()