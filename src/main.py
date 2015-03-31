# coding=utf-8
import argparse

if __name__ == '__main__':
    print "PICOOO"
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--data', dest='dataDir')
    args = argparser.parse_args()
    print args.dataDir
    #main(args)
