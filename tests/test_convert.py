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


def test_customDateFormat(tmpdir):
    inFilePath = tmpdir.mkdir("in").join("customdate.csv")
    inFilePath = str(inFilePath.realpath())
    outDir = tmpdir.mkdir("out")
    outFilePath = outDir.join("customdate.csv.tde")
    outFilePath = str(outFilePath.realpath())
    data = [['testcolumn']]
    testFormat = "%H:%M %d.%m.%Y"
    for rowIdx in range(0, testCsvLinesNumber):
        value = strTimeProp("00:00 1.1.2015","00:00 1.1.1960", testFormat, random.random())
        data.append([value])
    with open(inFilePath, 'w') as inFile:
        csvFile = csv.writer(inFile, delimiter=',')
        csvFile.writerows(data)
    typedefs = {'testcolumn':{'type':'datetime', 'format': testFormat}}
    src.convert2tde(inFilePath, outFilePath, typedefs)
    outSize = os.path.getsize(outFilePath)
    assert outSize > 0

@pytest.fixture(params=[{'type':'datetime', 'format': ''},{'type':'date', 'format': ''}, {'type':'date', 'format': 'ddda'}, {'type':'datetime', 'format': 'ddda'},{'type':'date', 'format': '%H'}, {'type':'datetime', 'format': '%H'}])
def invalidDateDef(request):
    return request.param

def test_customDateInvalidFormat(tmpdir, invalidDateDef):
    inFilePath = tmpdir.mkdir("in").join("customdate.csv" + str(random.random()))
    inFilePath = str(inFilePath.realpath())
    outDir = tmpdir.mkdir("out")
    outFilePath = outDir.join(str(random.random()) + "customdate.csv.tde" )
    outFilePath = str(outFilePath.realpath())
    data = [['testcolumn']]
    testFormat = "%H:%M %d.%m.%Y"
    for rowIdx in range(0, 3):
        value = strTimeProp("00:00 1.1.2015","00:00 1.1.1960", testFormat, random.random())
        data.append([value])
    with open(inFilePath, 'w') as inFile:
        csvFile = csv.writer(inFile, delimiter=',')
        csvFile.writerows(data)
    typedefs = {'testcolumn':invalidDateDef}
    with pytest.raises(SystemExit) as exc:
        src.convert2tde(inFilePath, outFilePath, typedefs)
    assert exc.value.code == 1



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

@pytest.fixture(params=['blabla','me dze  ra', '123 ddd', '-asdasd-1', 'aasd 12 -', '_','.asdasd', 'bla 1 2 _ -', '-', 'asd&sa', '&','()', '*d', '*', '#', '[]'])
def validCustomName(request):
    return request.param


def test_convertCustomNameOK(tmpdir, validCustomName):
    print "TMP DIR ", tmpdir
    inDataHeader = ['boolean']
    typedefs = {c: {'type':c} for c in inDataHeader} #map(lambda c: {'type':c}, inDataHeader)
    inDataGeneratorMap = {
        'boolean':  lambda: random.choice(['true', 'false']),
        'string':   lambda: 'test string'
    }
    inFilePath = tmpdir.mkdir("in").join("intable.csv")
    inFilePath = str(inFilePath.realpath())
    outDir = tmpdir.mkdir("out")
    outFilePath = outDir.join(validCustomName + '.tde')
    outFilePath = str(outFilePath.realpath())

    inFileData = []
    for rowIdx in range(0, 5):
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
