import pytest
import src
import csv
import random
import time
import os

def test_answer():
    assert 1 == 1


    #['boolean','number', 'decimal', 'date','datetime', 'string']

# args is [[columnvalues],[columnsvalues], [columnsvalues]]
def merge_columns(*args):
    cunt = 0
    result = []
    for arg in args:
        if len(arg) > cunt:
            cunt = len(arg)
    for i in range(0, cunt ):
        row = []
        for arg in args:
            if i < len(arg):
                row.append(arg[i])
            else:
                row.append("")
        result.append(row)
    return result

#check if file exists and is not empty
def file_exists(filepath):
    outSize = os.path.getsize(filepath)
    return outSize > 0

    #creates csv file from data and tmp dir,
    # @returns tuple inFilePath(path of csv file created),
    # and outFilePath(tde file path)
def createcsvfile(fname, tmpdir, header_row, data_rows):
    print "TMP DIR", tmpdir
    randstr = str(random.randint(1,100000))
    randstr = ""
    outdir = tmpdir.ensure_dir('out', 'files')
    indir = tmpdir.ensure_dir('in', 'tables')
    inFilePath = str(indir.join(randstr + fname).realpath())
    outFilePath = str(outdir.join(randstr + fname + ".tde").realpath())
    with open(inFilePath, 'w') as inFile:
        writer = csv.writer(inFile)
        writer.writerows([header_row])
        writer.writerows(data_rows)
    return inFilePath, outFilePath

# should not raise an exception, and pass ok
def test_emptyoutput(tmpdir):
    header = ["pokus"]
    data = []
    inFilePath, outFilePath = createcsvfile('pokus.csv', tmpdir, header, data)
    print inFilePath, outFilePath
    src.convert2tde(inFilePath, outFilePath, {})
    assert file_exists(outFilePath)

#test missing values, should pass filling null to tde file
def test_missing(tmpdir):
    c1 = ["1","2","","3","4"]
    c2 = ["asd", "dd", "asd"]
    c3 = ["1.0", "1", "20", "3.3", ""]
    c4 = ["", "True", "", "False"]
    c5 = ["2015-1-1", "", "", "", ""]
    c6 = ["", "2015-1-1 00:00:00", "", "", ""]
    data = merge_columns(c1, c2, c3, c4, c5, c6)
    print data
    header = ["c1", "c2", "c3", "c4", "c5", "c6"]
    inFilePath, outFilePath = createcsvfile('missing.csv', tmpdir, header, data)
    typedefs = {
        "c1":{"type": "number"},
        "c2":{"type": "string"},
        "c3":{"type": "decimal"},
        "c4": {"type": "boolean"},
        "c5": {"type": "date"},
        "c6": {"type": "datetime"}
    }
    src.convert2tde(inFilePath, outFilePath, typedefs)
    assert file_exists(outFilePath)

@pytest.fixture(params=[["1","2","3", "adsasd"], ["afsf"], ["1","asdasd"]])
def invalidNumbers(request):
    result = []
    for item in request.param:
        result.append([item])
    return result

def test_failedNumber(tmpdir, invalidNumbers):
    data = invalidNumbers
    header = ["number"]
    inFilePath, outFilePath = createcsvfile('invalidnumber.csv', tmpdir, header, data)
    typedefs = {"number":{"type":"number"}}
    with pytest.raises(SystemExit) as exc:
        src.convert2tde(inFilePath, outFilePath, typedefs)
    assert exc.value.code == 1


@pytest.fixture(params=[["1.2","2.1","3.2", "adsasd"], ["afsf"], ["1","asdasd"]])
def invalidDecimals(request):
    result = []
    for item in request.param:
        result.append([item])
    return result

def test_failedDecimal(tmpdir, invalidDecimals):
    data = invalidDecimals
    header = ["decimal"]
    inFilePath, outFilePath = createcsvfile('invaliddecimal.csv', tmpdir, header, data)
    typedefs = {"decimal":{"type":"decimal"}}
    with pytest.raises(SystemExit) as exc:
        src.convert2tde(inFilePath, outFilePath, typedefs)
    assert exc.value.code == 1
