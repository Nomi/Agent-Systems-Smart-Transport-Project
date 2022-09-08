## General Imports
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
from config import NUM_PASSENGERS_TO_GENERATE, NUM_BUSSES_TO_GENERATE
    #code here (num passengers, num busses, etc.)



#The part where the logic execution starts!
if __name__ == "__main__":
    '''
    Starts the agents and runs the main logic.
    '''
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== START ========'+Fore.RESET+Back.RESET)


    ###### BASIC SETUP ######
    #code here



    ###### !!!!!OTHER SUBSECTIONS HERE!!!!! ######
    centralAg = CentralAgent("nomanspadehw@01337.io/10","lololol",False)
    centralAg.set("id",0)
    centralAg.fillDetails([],[])
    centralFuture = centralAg.start()
    centralFuture.result()
    
    agent = PassengerAgent("nomanspadehw@01337.io/69","lololol",False)
    agent.set("id",1)
    agent.add_behaviour(RequestBus())#put this inside the bus class setup? like I did for central agent?
    agent.fillDetails("nomanspadehw@01337.io/10",centralAg.getRandomPassengerLocation(),"")
    future = agent.start()
    future.result()

    busAg = BusAgent("nomanspadehw@01337.io/91","lololol",False)
    busAg.set("id",2)
    busAg.fillDetails("nomanspadehw@01337.io/10")
    futureBus = busAg.start()
    futureBus.result()

    while agent.is_alive:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break

    ###### WINDING DOWN: ######
    print()
    quit_spade()
    sleep(1)
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== END ========'+Fore.RESET+Back.RESET)
