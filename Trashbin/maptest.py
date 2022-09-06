## General Imports
import random
import os
import sys
import spade
import time
import datetime
import asyncio
import traceback
import igraph
from dyngraphplot import DynGraphPlot
import networkx as nx


## Specific Imports
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import State, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, OneShotBehaviour
from spade.message import Message

from time import sleep
from colorama import Back,Fore,Style,init

## Importing our code:
import Agents.Central
import Agents.Bus
from Agents.Passenger import PassengerAgent, RequestBus
import Agents.AgentHelperFunctions

from helper import printArrMap



## initializing Colorama:
init(convert=True, autoreset=True)








# #The part where the logic execution starts!
# g = igraph.Graph()

# g.add_vertex("BS0")
# for i in range(1,11, 1):
#     g.add_vertex("BS"+str(i))
#     g.add_edge("BS"+str(i-1),"BS"+str(i))
# g.add_edge("BS10","BS0")
# print(g)

# layout = g.layout("kk")
# # igraph.plot(g, layout=layout)
# # import matplotlib.pyplot as plt
# # fig, ax = plt.subplots()
# # igraph.plot(g, layout=layout, target=ax)


gr = nx.Graph()
nodes=[("BS0",{"color": "red"})]
edges=[]
# gr.add_node(("BS0",{"color": "red"}))
for i in range(1,11, 1):
    # gr.add_node("BS"+str(i),{"color":"red"})
    nodes.append("BS"+str(i))
    # gr.add_edge("BS"+str(i-1),"BS"+str(i))
    edges.append(("BS"+str(i-1),"BS"+str(i)))
# gr.add_edge("BS10","BS0")
edges.append(("BS10","BS0"))

gr.add_nodes_from(nodes)
gr.add_edges_from(edges)

import matplotlib.pyplot as plt
G = nx.petersen_graph()
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
subax2 = plt.subplot(122)
nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

# zzz = [("PS1",{"color": "Red"}), ("PS2",{"color": "red"})]
# gr.add_nodes_from(zzz)
# import networkx as nx
# G = nx.Graph()
# G.add_node(1)
# G.add_nodes_from([2,3])
# G.add_edges_from([(1,2),(1,3)])
# G.clear()
# petersen=nx.petersen_graph()
# plot = DynGraphPlot(petersen)#(G)

# gr.add_edges_from(edges)
# map = [
#         [' ',' ','P',' '],
#         ['-','-','-','-'],
#         [' ','B',' ',' '],
#         ['-','-','-','-'],
#         [' ',' ',' ',' ']
#       ]
# printArrMap(map)

plot = DynGraphPlot(gr)
input()
# update nodes and edges in the graph
new_nodez = ["PS1", "PS2"]
plot.update(new_nodes= new_nodez)

# wait before exiting
input()