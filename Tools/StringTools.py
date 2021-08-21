

def secondsToTimeDescription(elapsedSeconds):
    return str(int(elapsedSeconds/3600)) \
            + "h "  \
            + str(int((elapsedSeconds/60) % 60)) \
            + "m " \
            + str((elapsedSeconds % 60)) \
            + "s"


def getFilenameFromFullName(filename):
    splt = filename.split('/')
    return splt[len(splt)-1]

def getTickerFromFilename(filename):
    lastpart = getFilenameFromFullName(filename)
    return lastpart[(lastpart.find('_')+1):lastpart.find('__')]

def getDateFromFilename(filename):
    lastpart = getFilenameFromFullName(filename)
    return lastpart[lastpart.find('__')+2:lastpart.find('.csv')]


# returns: (filename, ticker, datestr)
def getInfoFromFullFilename(filename):
    splt = filename.split('/')
    lastpart = splt[len(splt)-1]

    return lastpart, \
        lastpart[(lastpart.find('_')+1):lastpart.find('__')], \
        lastpart[lastpart.find('__')+2:lastpart.find('.csv')]
