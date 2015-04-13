import pytest
import src
import csv
import random
import time
import os
# TEST def convert2tde(inFilePath, outFilePath, typedefs):
testCsvLinesNumber = 20

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))


def test_answer():
    assert 1 == 1


# should pass
def test_convertOK(tmpdir):
    print "TMP DIR ", tmpdir
    inDataHeader = ['boolean','number', 'decimal', 'date','datetime', 'string']
    typedefs = {c: {'type':c} for c in inDataHeader} #map(lambda c: {'type':c}, inDataHeader)
    inDataGeneratorMap = {
        'boolean':  lambda: random.choice(['true', 'false']),
        'number':   lambda: str(random.randrange(0,1000)),
        'decimal':  lambda: str(random.random()),
        'date':     lambda: strTimeProp("2015-1-1","1960-1-1","%Y-%m-%d", random.random()),
        'datetime': lambda: strTimeProp("2015-1-1 00:00:00","1960-1-1 00:00:00", "%Y-%m-%d %H:%M:%S", random.random()),
        'string':   lambda: 'test string'
    }
    inFilePath = tmpdir.mkdir("in").join("intable.csv")
    inFilePath = str(inFilePath.realpath())
    outDir = tmpdir.mkdir("out")
    outFilePath = outDir.join("intable.csv.tde")
    outFilePath = str(outFilePath.realpath())

    inFileData = []
    for rowIdx in range(0, testCsvLinesNumber):
        row = []
        for column in inDataHeader:
            row.append(inDataGeneratorMap[column]())
        inFileData.append(row)

    with open(inFilePath, 'w') as inFile:
        csvFile = csv.writer(inFile, delimiter=',')
        csvFile.writerows([inDataHeader])
        csvFile.writerows(inFileData)

    src.convert2tde(inFilePath, outFilePath, typedefs)
    outSize = os.path.getsize(outFilePath)
    assert outSize > 0
