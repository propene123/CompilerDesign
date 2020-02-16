import sys

def readInFile(fileName):
    pass;


if(len(sys.argv) < 2):
    sys.exit('no input file specified')

inFile = sys.argv[1]
fileDict = readInFile(inFile)
