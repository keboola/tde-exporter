# coding=utf-8
import argparse
import subprocess
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
import uploadTasks
import Exceptions
import re
import pipes

csvDelimiter = ','
csvQuoteChar = '"'
defaultTags = ['table-export', 'tde']
maxFileNameLen = 150
customFileNameRegex = "^[a-zA-Z_0-9\- \(\)\.]+$"

def handleApplicationError():
    """
    print application error and stack trace to the stderr
    terminate application with return code -1(127)

    """
    print "Unexpected error:", sys.exc_info()[0]
    print '-'*50
    traceback.print_exc(file=sys.stderr)
    print '-'*50
    sys.exit(-1)

def convert2tde(inFilePath, outFilePath, typedefs):
    """
    convert file from @inFilePath to tde to @outFilePath
    """

    # _csv.Error: field larger than field limit (131072)
    # https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
    csv.field_size_limit(sys.maxint)

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
    except csv.Error as e:
        print e
        sys.exit(1)
    except:
        handleApplicationError()


def getParameters(config, path):
    """
    For all @components from @config:params:uploadTasks call \run with token and runId
    that takes all files filtered by this job runId
    """
    try:
        return reduce(lambda d, k: d[k], ['parameters'] + path, config)
    except:
        return None

def getOutputFileName(config, tableId):
    """
    returns (custom or default) name of the output file name for @tableId
    """
    tdeName = getParameters(config, ['tables', tableId, 'tdename'])
    defaultName = tableId + '.tde'
    name = tdeName or defaultName
    if name.endswith('.tde'):
        return name
    else:
        return name + '.tde'

def getParentRunIdTag():
    """
    return environment var parent runId prefixed with runId-
    runId-<parent_run_id>
    if no run id present return None
    """
    try:
        runid = os.environ['KBC_RUNID']
        return 'runId-' + runid.split('.')[0]
    except:
        return None

def getRunId():
    """
    return environment var runId or None if not present
    """
    try:
        runid = os.environ['KBC_RUNID']
        return runid
    except:
        return None

def getExporterRunId():
    """
    return environment var runId or None if not present
    """
    try:
        return 'exporterRunId-' + getRunId()
    except:
        return None

def getToken():
    """
    return environment var kbc token or None if not present
    """
    try:
        token = os.environ['KBC_TOKEN']
        return token
    except:
        debug('Error: token is missing')
        exit(-1);


def createManifest(outFilePath, outFileName, tags):
    """
    create yaml manifest file for kbc upload(output mapping)
    """
    runidtag = []
    runid = getParentRunIdTag()
    if runid:
        debug('runid tag:', runid)
        runidtag = [runid]
    resultTags = list(set(defaultTags + tags + runidtag + [getExporterRunId()]))
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
    return yaml.load(open(dataDir + '/config.yml', 'r'), Loader=yaml.FullLoader)

def checkConfig(config):
    """
    check config object and return True/False
    """
    inTables = config['storage']['input']['tables']
    result = True
    # input mapping specified?
    if not inTables:
        print 'No input tables specified.'
        return False
    sources = map(lambda t: t['source'], inTables)

    for tableId in sources:
        tdeName = getOutputFileName(config, tableId)
        msg = checkOutputName(tdeName)
        if msg != None:
            debug('Output tde file name for ' + tableId + ' is invalid:', msg)
            return False
    #customNames = getParameters(config, ['tables'])
    # customNamesKeys = customNames.keys()


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
def createOutDir(dataDir):
    outDirPath = ''

def uploadFiles(sourceFolder, token, runId):
    """
    send files to file uploads of the kbc project
    """
    #sourceFolder = '/data/tde-files'
    debug('Sending files to Keboola storage started')
    args = ["php", "php/src/run.php", token, sourceFolder, runId]
    if not runId:
        args = ["php", "php/src/run.php", token, sourceFolder]
    code = subprocess.call(args)
    if code != 0:
        raise Exception('Error uploading files')
    debug('Sending files to Keboola storage finished')
    return True

def checkOutputName(name):
    if len(name) > maxFileNameLen:
        return 'Filename too long, max 150 characters are allowed'
    if re.match(customFileNameRegex ,name) == None:
        return name + ': Invalid string, only alphanumeric characters, space, . ()-_ are allowed'
    return None


def emptydir(path):
    """
    deletes the content of the directory given path by @top param
    """
    code = subprocess.call("rm %s* -rf" % tuple(map(pipes.quote, [path])), shell=True)
    if code != 0:
        raise Exception('Error removing files from '  + path)
    return True

def main(args):
    """
    main control method
    """
    token = getToken()
    runId = getRunId()
    config = loadConfigFile(args.dataDir)

    inTables = config['storage']['input']['tables']
    if not checkConfig(config):
        exit(1)
    inPathPrefix = args.dataDir + '/in/tables/'
    outPathPrefix = '/data/out/files/'
    #create output dir if not exists
    if not os.path.exists(outPathPrefix):
        os.makedirs(outPathPrefix)
    inFilesPaths = inTables

    for table in inFilesPaths:
        fileName = table['source']
        if 'destination' in table:
            fileName = table['destination']
        inFilePath = inPathPrefix + fileName
        outFileName = getOutputFileName(config, table['source'])
        outFilePath = outPathPrefix + outFileName
        typedefs = getParameters(config, ['typedefs', table['source']])
        convert2tde(inFilePath, outFilePath, typedefs or {})
        tags = getParameters(config,['tags'])
        createManifest(outFilePath, outFileName, tags or [])

    try:
        uploadFiles(outPathPrefix, token, runId)
        uploadTasks.runUploadTasks(config, token, runId)
        emptydir(outPathPrefix)
    except Exceptions.UploadException as e:
        print e
        sys.exit(1)
    except:
        handleApplicationError()



#entry point
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--data', dest='dataDir')
    args = argparser.parse_args()
    main(args)
    debug("FINISHED")
