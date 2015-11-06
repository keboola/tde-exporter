# coding=utf-8
import argparse
import yaml
import csv2tde
import csv
import sys
import os
import traceback
import codecs
from dataextract import TableauException
from logger import debug
import itertools

csvDelimiter = ','
csvQuoteChar = '"'
defaultTags = ['table-export', 'tde']


def convert2tde(inFilePath, outFilePath, typedefs):
    try:
        debug( "converting" +  inFilePath)
        with open(inFilePath, 'rb') as inFile:
            lazyLines = itertools.imap(lambda line: line.replace('\0', ''), inFile)
            csvReader = csv.reader(lazyLines,
                                   delimiter = csvDelimiter, quotechar = csvQuoteChar)
            csv2tde.convert(csvReader, outFilePath, typedefs)
    except ValueError as e:
        print "Error:",e
        sys.exit(1)
    except TableauException as e:
        print e
        sys.exit(1)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print '-'*50
        traceback.print_exc(file=sys.stderr)
        print '-'*50
        sys.exit(-1)


def getParameters(config, path):
    try:
        return reduce(lambda d, k: d[k], ['parameters'] + path, config)
    except:
        return None

def getRunId():
    try:
        runid = os.environ['KBC_RUNID']
        return 'runId-' + runid.split('.')[0]
    except:
        return None


def createManifest(outFilePath, outFileName, tags):
    runidtag = []
    runid = getRunId()
    if runid:
        debug('runid tag:', runid)
        runidtag = [runid]
    resultTags = list(set(defaultTags + tags + runidtag))
    manifest = {
        'is_permanent': True,
        'is_public': False,
        'tags': resultTags,
        'is_encrypted': True
    }

    debug('tags ', resultTags)
    debug("writing manifest " + outFileName)
    with open(outFilePath + '.manifest', 'w') as manifestFile:
        yaml.dump(manifest, manifestFile)

def loadConfigFile(dataDir):
    return yaml.load(open(dataDir + '/config.yml', 'r'))

def checkConfig(config):
    inTables = config['storage']['input']['tables']
    result = True
    # input mapping specified?
    if not inTables:
        print 'No input tables specified.'
        return False
    sources = map(lambda t: t['source'], inTables)
    #if no typedefs specified we leave with true
    typedefs = getParameters(config, ['typedefs'])
    if not typedefs:
        return True
    sources = set(sources)
    typedefs = set(typedefs.keys())
    def setstr(s):
        return ", ".join(str(i) for i in s)
    #if some typedefs does not exists in input mapping sources
    result = typedefs.issubset(sources)
    if not result:
        print "parameter typedefs contains not existing source, got input sources:", setstr(sources), "and got typedefs sources:", setstr(typedefs)

    #columns types must be valid if specified
    typedefs = getParameters(config, ['typedefs'])
    for source in sources:
        if source in typedefs:
            for column in typedefs[source].values():
                if column['type'].lower() not in csv2tde.schemaIniTypeMap:
                    result = False
                    print 'Unsupported column data type(',column['type'],') for', source
    return result


def main(args):
    config = loadConfigFile(args.dataDir)
    inTables = config['storage']['input']['tables']
    if not checkConfig(config):
        exit(1)
    inPathPrefix = args.dataDir + '/in/tables/'
    outPathPrefix = args.dataDir + '/out/files/'
    inFilesPaths = inTables
    for table in inFilesPaths:
        fileName = table['source']
        if 'destination' in table:
            fileName = table['destination']
        inFilePath = inPathPrefix + fileName
        outFileName = table['source'] + '.tde'
        outFilePath = outPathPrefix + outFileName
        typedefs = getParameters(config, ['typedefs', table['source']])
        convert2tde(inFilePath, outFilePath, typedefs or {})
        tags = getParameters(config,['tags'])
        createManifest(outFilePath, outFileName, tags or [])


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--data', dest='dataDir')
    args = argparser.parse_args()
    main(args)
    debug("FINISHED")
