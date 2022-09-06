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
# from Faker import faker()



### Global Variables

## States:
LOOKING_FOR_RIDE = "LOOKING_FOR_RIDE" #yellow node
WAITING_FOR_RIDE = "WAITING_FOR_RIDE" #blue node
RIDING = "RIDING"
GETTING_OFF= "GETTING_OFF"
FINISHED="FINISHED"


class PassengerAgent(Agent):
    destination=""
    # location=""
    centralAgentAddress=""
    timeOfStart=time.time()
    timelimit=20#seconds
    succesfullyCompleted=False
    currentColor = ""
    position = dict({
        "x": -1,
        "y": -1
    })

    async def setup(self):
        self.add_behaviour(TransitFiniteStates())
        print(Fore.CYAN + f"Passenger Agent {self.get('id')} : STARTING     [jid: {str(self.jid)}]" + Fore.RESET)
        self.timeOfStart=time.time()
        return 0
        
    def fillDetails(self, CentralAgentXMPPID: string, position:dict, destination:string):
        self.centralAgentAddress=CentralAgentXMPPID
        self.position=position
        self.destination=destination

    def getCurrentColor(self):
        return self.currentColor


class RequestBus(OneShotBehaviour):
    async def on_start(self):
        self.agent.currentColor = "yellow"
    async def run(self):
        msg = Message(to=self.agent.centralAgentAddress)
        msg.body="P:"+str(self.agent.timelimit)+":"+str(self.agent.position["x"])+":"+str(self.agent.position["y"])
        await self.send(msg)
        #SEND MESSAGE TO ORGANIZER LOOKING FOR BUS
        print("Request bus not implemented.")


class TransitFiniteStates(FSMBehaviour):
    async def on_start(self):
        self.add_state(name=LOOKING_FOR_RIDE, state=LookForBus_StateBehavior(), initial=True)
        self.add_state(name=WAITING_FOR_RIDE, state=WaitingForBus_StateBehavior())
        self.add_state(name=RIDING, state=RidingBus_StateBehavior())
        self.add_state(name=GETTING_OFF, state=GettingOff_StateBehavior())
        self.add_state(name=FINISHED, state=Finished_StateBehavior())
        self.add_transition(source=LOOKING_FOR_RIDE, dest=LOOKING_FOR_RIDE)#
        self.add_transition(source=LOOKING_FOR_RIDE, dest=WAITING_FOR_RIDE)#
        self.add_transition(source=WAITING_FOR_RIDE, dest=WAITING_FOR_RIDE)
        self.add_transition(source=WAITING_FOR_RIDE, dest=RIDING)
        self.add_transition(source=RIDING, dest=RIDING)
        self.add_transition(source=RIDING, dest=GETTING_OFF)
        self.add_transition(source=GETTING_OFF, dest=FINISHED)
        self.add_transition(source=FINISHED, dest=FINISHED)
        self.add_transition(source=LOOKING_FOR_RIDE, dest=FINISHED)#
        self.add_transition(source=WAITING_FOR_RIDE, dest=FINISHED)#

class LookForBus_StateBehavior(State): #FIN
    async def on_end(self):
        self.agent.currentColor = "blue"
        
    async def run(self):
        notFoundBus = True
        # self.agent.succesfullyCompleted=True #was just here for debug.
        print("DEBUG: looking for bus.")
        try:
            msg = await self.receive(timeout=10)
            if msg:
                if(msg.body=="--[ACCEPT]--"):
                    print("debug passenger: ride found")
                    notFoundBus=False
                    self.set_next_state(WAITING_FOR_RIDE)
                elif(msg.body=="--[REJECT]--"):
                    self.set_next_state(FINISHED)
            
            if(notFoundBus):
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

            searchTimeSoFar = int(time.time() - self.agent.timeOfStart)
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
                msg = Message(to=self.agent.centralAgentAddress)
                msg.body='--[CANCEL]--'
            #shut down??? cleanup???
        except:
            traceback.print_exc()