def splitListIntoChonks(list, length):
    toreturn = [] 
    for i in range(0, len(list), length):
        toreturn.append(list[i:i + length])
    return toreturn 
