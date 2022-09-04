def printArrMap(arrMap:list):
    for i in range(0,arrMap.__len__()):
        for j in range(0,arrMap[i].__len__()):
            print(arrMap[i][j], end='')
        print()