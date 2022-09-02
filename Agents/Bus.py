###General Imports
from queue import Full
import random
import os
import sys
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



### Global Variables
MAXPASSENGERS = 2



## States:
MOVING = "MOVING"
PICKING_UP_CLIENT = "PICKING_UP_CLIENT" #Do not disturb
DROPPING_OFF_CLIENT = "DROPPING_OFF_CLIENT" #Do not disturb when near destination of passenger.
FULL_BUSS = "FULL_BUSS" #Do not disturb
FINAL_STOP = "FINAL_STOP"
AT_BUS_STOP = "AT_BUS_STOP"

class BusAgent(Agent):
    route=[]
    #finalStopIndex = -1 #use (route.count-1) instead
    currentStopIndex = -1
    centralAgentAddress=""
    passengerCount=0
    timeOfStart=time.time()

    async def setup(self):
        self.add_behaviour(TransitFiniteStates())
        print(Fore.LIGHTRED_EX + f"Bus Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        return 0
        
    def fillDetails(self, CentralAgentXMPPID: string, route:list):
        self.centralAgentAddress=CentralAgentXMPPID
        self.route=route
        self.currentStopIndex=0

class TransitFiniteStates(FSMBehaviour):
    async def on_start(self):
        self.add_state(name=AT_BUS_STOP, state=AtBusStop_StateBehavior(), initial=True)
        self.add_state(name=MOVING, state=Moving_StateBehavior())
        self.add_state(name=PICKING_UP_CLIENT, state=WaitingForBus_StateBehavior())
        self.add_state(name=DROPPING_OFF_CLIENT, state=RidingBus_StateBehavior())
        self.add_state(name=FULL_BUSS, state=GettingOff_StateBehavior())
        self.add_state(name=FINAL_STOP, state=GettingOff_StateBehavior())
        
        self.add_transition(source=MOVING, dest=AT_BUS_STOP)
        self.add_transition(source=AT_BUS_STOP, dest=PICKING_UP_CLIENT)
        self.add_transition(source=AT_BUS_STOP, dest=DROPPING_OFF_CLIENT)
        self.add_transition(source=MOVING, dest=FULL_BUSS)
        self.add_transition(source=MOVING, dest=FINAL_STOP)
        self.add_transition(source=PICKING_UP_CLIENT, dest=AT_BUS_STOP)
        self.add_transition(source=AT_BUS_STOP, dest=MOVING)
        self.add_transition(source=AT_BUS_STOP, dest=FULL_BUSS)
        self.add_transition(source=FULL_BUSS, dest=DROPPING_OFF_CLIENT)
        self.add_transition(source=DROPPING_OFF_CLIENT, dest=AT_BUS_STOP)
        self.add_transition(source=MOVING, dest=FINAL_STOP)
        self.add_transition(source=FULL_BUSS, dest=FINAL_STOP)

        self.add_transition(source=MOVING, dest=MOVING)
        self.add_transition(source=PICKING_UP_CLIENT, dest=PICKING_UP_CLIENT)
        self.add_transition(source=DROPPING_OFF_CLIENT, dest=DROPPING_OFF_CLIENT)
        self.add_transition(source=FULL_BUSS, dest=FULL_BUSS)
        self.add_transition(source=FINAL_STOP, dest=FINAL_STOP)
        self.add_transition(source=AT_BUS_STOP, dest=AT_BUS_STOP)

class AtBusStop_StateBehavior(State): #FIN
    async def run(self):

        print("DEBUG: Checking if we're assigned passengers (10 secs).")
        try:
            msg = await self.receive(timeout=10)
            if msg: #should contain the graph position of the passenger's position somehow
                message = msg.body.split(':')
                baserouteidx = message[0]
                detourrouteidx = message[1]
                self.agent.route.

            searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
            print(searchTimeSoFar)
            if(searchTimeSoFar >= self.agent.timelimit):
                #NOTIFY CENTRAL AGENT TO CANCEL??
                self.set_next_state(FINISHED)
            else:
                self.set_next_state(LOOKING_FOR_RIDE)
                await asyncio.sleep(2)
        except:
            traceback.print_exc()

class Moving_StateBehavior(State): #FIN
    async def run(self):
        # self.agent.succesfullyCompleted=True #was just here for debug.
        print("DEBUG: looking for bus.")
        try:
            msg = await self.receive(timeout=10)
            if msg:
                if(msg.body=="--[ACCEPT]--"):
                    self.set_next_state(WAITING_FOR_RIDE)
                elif(msg.body=="--[REJECT]--"):
                    self.set_next_state(FINISHED)
            
            searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
            print(searchTimeSoFar)
            if(searchTimeSoFar >= self.agent.timelimit):
                #NOTIFY CENTRAL AGENT TO CANCEL??
                self.set_next_state(FINISHED)
            else:
                self.set_next_state(LOOKING_FOR_RIDE)
                await asyncio.sleep(2)
        except:
            traceback.print_exc()

class WaitingForBus_StateBehavior(State):
    async def run(self):
        try:
            msg = await self.receive()
            if msg:
                if(msg.body=="--[BUS_HERE]--"):
                    self.set_next_state(RIDING)

            searchTimeSoFar = int(time.now() - self.agent.timeOfStart)
            if(searchTimeSoFar >= self.agent.timelimit):
                #NOTIFY CENTRAL AGENT TO CANCEL??
                self.set_next_state(FINISHED)

            self.set_next_state(WAITING_FOR_RIDE)
            await asyncio.sleep(2)
        except:
            traceback.print_exc()

class RidingBus_StateBehavior(State):
    async def run(self):
        try:
            msg = await self.receive()
            if msg:
                if(msg.body=="--[REACHED_DESTINATION]--"):
                    self.set_next_state(GETTING_OFF)
                    return
            self.set_next_state(RIDING)
            await asyncio.sleep(2)
        except:
            traceback.print_exc()

class GettingOff_StateBehavior(State):
    async def run(self):
        try:
            self.agent.succesfullyCompleted=True
            ##Send message you've gotten off
            self.set_next_state(FINISHED)
            await asyncio.sleep(2)
        except:
            traceback.print_exc()

class Finished_StateBehavior(State):
    async def run(self):
        try:
            if(self.agent.succesfullyCompleted):
                print(Fore.CYAN + f"Passenger Agent {self.get('id')} : FINISHED MY JOURNEY     [jid: {str(self.agent.jid)}]" + Fore.RESET)
            else:
                print(Fore.CYAN + f"Passenger Agent {self.get('id')} : FAILED TO TRAVEL     [jid: {str(self.agent.jid)}]" + Fore.RESET)
            #shut down??? cleanup???
        except:
            traceback.print_exc()