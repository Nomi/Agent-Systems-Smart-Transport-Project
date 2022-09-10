#####################################################
#####################################################
##                  CONFIGURATION                  ##
#####################################################
#####################################################

''' GENERAL '''
JID_BASE="nomanspadehw@01337.io" #Jabber ID


''' main.py '''
NUM_PASSENGERS_TO_GENERATE = 9
NUM_BUSSES_TO_GENERATE = 4
#code here (num passengers, num busses, etc.)


''' Central.py '''
ARRMAP_HEIGHT = 16 #4 #7 #19 #try to have this be odd (or even?)
ARRMAP_WIDTH = 50 #5 #10 #30 #100


''' Bus.py '''
MAX_PASSENGERS = 1
LAST_STOP = ARRMAP_WIDTH -1
SYMBOL_FULLBUSS = ">"
SYMBOL_NOTFULLBUSS = "+"
TIME2SLEEP4 = 3 #1 #number of seconds needed per 1 index movement.

''' Passenger.py '''


''' AgentHelperFunctions.py '''


''' helper.py '''


''' Misc. '''
SECOND2NANOSECOND = 1000000000