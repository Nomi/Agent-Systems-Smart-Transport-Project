#General Imports
import random
import os
import sys
import spade
import time
import datetime
import asyncio
import traceback



#Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init



## Global Variables:

#States:
BUSY="BUSY" #one person at a time for now.
FREE="FREE"