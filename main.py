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
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init

## Importing our code:
import Agents.CentralAgent
import Agents.BusAgent
import Agents.PassengerAgent
import Agents.AgentHelperFunctions


## initializing Colorama:
init(convert=True, autoreset=True)








#The part where the logic execution starts!
if __name__ == "__main__":
    '''
    Starts the agents and runs the main logic.
    '''
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== START ========'+Fore.RESET+Back.RESET)



    ###### CONFIGURATION ######
    #code here



    ###### BASIC SETUP ######
    #code here



    ###### !!!!!OTHER SUBSECTIONS HERE!!!!! ######



    ###### WINDING DOWN: ######
    print()
    quit_spade()
    sleep(1)
    print(Back.LIGHTGREEN_EX+Fore.RED+'======== END ========'+Fore.RESET+Back.RESET)
