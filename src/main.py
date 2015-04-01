# coding=utf-8
import argparse
import yaml
import csv2tde
import csv

csvDelimiter = ','
csvQuoteChar = '"'
defaultTags = ['table-export', 'tde']


def debug(msg):
    print msg + '\n\n'


def convert2tde(inFilePath, outFilePath):
    debug( "converting" +  inFilePath)
    csvReader = csv.reader(open(inFilePath, 'rb'),
                           delimiter = csvDelimiter, quotechar = csvQuoteChar)
    csv2tde.convert(csvReader, outFilePath)



def createManifest(outFilePath, outFileName):
    manifest = {
        'is_permanent': True,
        'is_public': False,
        'tags': ['table-export', 'tde']
    }
    debug("writing manifest " + outFileName)
    with open(outFilePath + '.manifest', 'w') as manifestFile:
        yaml.dump(manifest, manifestFile)


def main(args):
    config = yaml.load(open(args.dataDir + '/config.yml', 'r'))
    inTables = config['storage']['input']['tables']
    inPathPrefix = args.dataDir + '/in/tables/'
    outPathPrefix = args.dataDir + '/out/files/'
    #print inTables.values()
    inFilesPaths = inTables #[ t  for t in inTables.values()]
    for table in inFilesPaths:
        inFilePath = inPathPrefix + table['source']
        outFileName = table['source'] + '.tde'
        outFilePath = outPathPrefix + outFileName
        convert2tde(inFilePath, outFilePath)
        createManifest(outFilePath, outFileName)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--data', dest='dataDir')
    args = argparser.parse_args()
    main(args)
    debug("FINISHED")
