## General Imports
from ast import Pass
import random
import os
import sys
import spade
import time
import datetime
import asyncio
import traceback



## Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init

## Importing our code:
from Agents.Central import CentralAgent
from Agents.Bus import BusAgent
from Agents.Passenger import PassengerAgent, RequestBus
import Agents.AgentHelperFunctions


## initializing Colorama:
init(convert=True, autoreset=True)



## CONFIGURATION ##
from config import NUM_PASSENGERS_TO_GENERATE, NUM_BUSSES_TO_GENERATE, JID_BASE, JID_PASSWORD
    #code here (num passengers, num busses, etc.)



#The part where the logic execution starts!
if __name__ == "__main__":
    '''
    Starts the agents and runs the main logic.
    '''
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== START ========'+Fore.RESET+Back.RESET)


    ###### BASIC SETUP ######
    agentId = 0
    centralAgentJidAlias = 10
    busJidAlias = 1000 #range start
    passJidAlias = 2000 #range start




    ###### Central Agent setup and start ######
    centralAg = CentralAgent(f"{JID_BASE}/{centralAgentJidAlias}",JID_PASSWORD,False)
    centralAg.set("id",agentId)
    # centralAg.fillDetails([],[])
    centralFuture = centralAg.start()
    centralFuture.result()
    
    ###### Spawning busses ######
    for i in range(0,NUM_BUSSES_TO_GENERATE):
        agentId+=1
        busAg = BusAgent(f"{JID_BASE}/{busJidAlias}",JID_PASSWORD,False)
        busAg.set("id",agentId)
        busAg.fillDetails(f"{JID_BASE}/{centralAgentJidAlias}",2+i*3,0)
        futureBus=busAg.start()
        futureBus.result()
        busJidAlias+=1
    # busAg = BusAgent(f"{JID_BASE}/91","lololol",False)
    # busAg.set("id",2)
    # busAg.fillDetails(f"{JID_BASE}/10",2,0)
    # futureBus = busAg.start()
    # futureBus.result()

    passengersWaitingToSpawnListButWithoutDetails:list = []
    ###### Preparing Passenger Agents ######
    for i in range(0,NUM_PASSENGERS_TO_GENERATE):
        agentId+=1
        agent:PassengerAgent = PassengerAgent(f"{JID_BASE}/{passJidAlias}",JID_PASSWORD,False)
        agent.set("id",agentId)
        agent.add_behaviour(RequestBus())#put this inside the bus class setup? like I did for central agent?
        passengersWaitingToSpawnListButWithoutDetails.append(agent)
        passJidAlias+=1
    # agent = PassengerAgent(f"{JID_BASE}/69","lololol",False)
    # agent.set("id",1)
    # agent.add_behaviour(RequestBus())#put this inside the bus class setup? like I did for central agent?
    # agent.fillDetails(f"{JID_BASE}/{centralAgentJidAlias}",centralAg.getRandomPassengerLocation(),"")
    # future = agent.start()
    # future.result()
    
    ## For testing:
    # agent = PassengerAgent(f"{JID_BASE}/69","lololol",False)
    # agent.set("id",1)
    # agent.add_behaviour(RequestBus())#put this inside the bus class setup? like I did for central agent?
    # agent.fillDetails(f"{JID_BASE}/{centralAgentJidAlias}",centralAg.getRandomPassengerLocation(),"",True)
    # future = agent.start()
    # future.result()

    random.seed(time.time_ns())
    numPassSpawned = 0
    while centralAg.is_alive:
        try:
            #Spawning passenger agents:
            if numPassSpawned < NUM_PASSENGERS_TO_GENERATE:
                numPassAgentsToGenThisTurn = random.randint(0,3)
                if(numPassAgentsToGenThisTurn>0):
                    for i in range(0,numPassAgentsToGenThisTurn):
                        passengersWaitingToSpawnListButWithoutDetails[numPassSpawned].fillDetails(f"{JID_BASE}/{centralAgentJidAlias}",centralAg.getRandomPassengerLocation(),"")
                        future = passengersWaitingToSpawnListButWithoutDetails[numPassSpawned].start()
                        future.result() 
                        numPassSpawned+=1
                        if(numPassSpawned==NUM_PASSENGERS_TO_GENERATE):
                            break
            time.sleep(1)
        except KeyboardInterrupt:
            centralAg.stop()
            break

    ###### WINDING DOWN: ######
    print()
    quit_spade()
    sleep(1)
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== END ========'+Fore.RESET+Back.RESET)
