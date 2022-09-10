#####################################################
#####################################################
##                  CONFIGURATION                  ##
#####################################################
#####################################################

''' GENERAL '''
JID_BASE="nomanspadehw@01337.io" #Jabber ID
JID_PASSWORD = "lololol"


''' main.py '''
NUM_PASSENGERS_TO_GENERATE:int = 6 #10 #40 is the upper limit
NUM_BUSSES_TO_GENERATE:int = 4     #40 is the upper limit
#code here (num passengers, num busses, etc.)


''' Central.py '''
ARRMAP_HEIGHT = 16 #4 #7 #19 #try to have this be odd (or even?)
ARRMAP_WIDTH = 30 #5 #10 #30 #100
ENABLE_PASSENGER_SPACE_RESERVATION = True


''' Bus.py '''
MAX_PASSENGERS = 2
LAST_STOP = ARRMAP_WIDTH -1
SYMBOL_FULLBUSS = ">"
SYMBOL_NOTFULLBUSS = "+"
TIME2SLEEP4 = 3 #1 #number of seconds needed per 1 index movement.

''' Passenger.py '''


''' AgentHelperFunctions.py '''


''' helper.py '''


''' Misc. '''
SECOND2NANOSECOND = 1000000000