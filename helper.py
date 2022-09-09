from turtle import position
from numpy import array
import random
import time

def getRandomPassengerLocation(arrMap:list) -> dict:
    random.seed(time.time_ns)
    positionNotFound = True
    maxX = arrMap[0].__len__()-1
    maxY = arrMap.__len__()-1
    x=0
    y=0
    while(positionNotFound):
        x = random.randint(0,maxX)
        y = random.randint(0,maxY)
        if(arrMap[y][x]=='='):
            y=y+1
        if(arrMap[y][x]==' '):
            positionNotFound = False
    return dict({"x":x, "y": y})


class coordinates:
    x:int #width of 2d array
    y:int #height of 2d array
    def __init__(self, x:int, y:int):
        self.x=x
        self.y=y