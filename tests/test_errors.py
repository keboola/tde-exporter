import pytest
import src
import csv
import random
import time
import os

def test_answer():
    assert 1 == 1


    #['boolean','number', 'decimal', 'date','datetime', 'string']

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
