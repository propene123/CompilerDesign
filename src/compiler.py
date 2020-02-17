import sys

CONNSTRINGS = ['AND', 'OR', 'IMPLIES', 'IFF', 'NOT']
QSTRINGS = ['EXISTS', 'FORALL']


def read_in_file(file_name, symTable):
    try:
        with open(file_name) as inFile:
            lines = list(inFile)
    except IOError:
        sys.exit('Could not open input file.')
    for line in lines:
        lineSplit = line.split(':')
        if lineSplit[0].strip() == 'variables':
            if len(lineSplit) == 2:
                variables = lineSplit[1].split()
                for v in variables:
                    if v in symTable:
                        sys.exit(
                            f'Variable {v} is already defined as a {symTable[v][0]}')
                    else:
                        symTable[v] = ['VARIABLE']
        elif lineSplit[0].strip() == 'constants':
            if len(lineSplit) == 2:
                constants = lineSplit[1].split()
                for c in constants:
                    if c in symTable:
                        sys.exit(
                            f'Constant {c} is already defined as a {symTable[c][0]}')
                    else:
                        symTable[c] = ['CONSTANT']

        elif lineSplit[0].strip() == 'equality':
            if len(lineSplit) != 2 or len(lineSplit[1].split()) != 1:
                sys.exit(
                    'Exactly 1 equality symbol must be sepecified in an input file')
            eq = lineSplit[1].split()[0]
            if eq in symTable:
                sys.exit(
                    f'Equality {eq} is already defined as a {symTable[eq][0]}')
            else:
                symTable[eq] = ['EQUALITY']
        elif lineSplit[0].strip() == 'connectives':
            if len(lineSplit) != 2 or len(lineSplit[1].split()) != 5:
                sys.exit('Exactly 5 equality symbols must be defined')
            connectives = lineSplit[1].split()
            count = 0
            for c in connectives:
                if c in symTable:
                    sys.exit(
                        f'Connective {c} is already defined as a {symTable[c][0]}')
                else:
                    symTable[c] = ['CONNECTIVE', CONNSTRINGS[count]]
                    count += 1

        elif lineSplit[0].strip() == 'quantifiers':
            if len(lineSplit) != 2 or len(lineSplit[1].split()) != 2:
                sys.exit('Exactly 2 quantifiers must be sepecified')
            quantifiers = lineSplit[1].split()
            count = 0
            for q in quantifiers:
                if q in symTable:
                    sys.exit(
                        f'Quantifier {q} is already defined as a {symTable[q][0]}')
                else:
                    symTable[q] = ['QUANTIFIER', QSTRINGS[count]]
                    count += 1


if len(sys.argv) < 2:
    sys.exit('no input file specified')
symTable = {'(': ['SEPARATOR', 'OB'], ')': [
    'SEPARATOR', 'CB'], ',': ['SEPARATOR', 'C']}
INFILE = sys.argv[1]
read_in_file(INFILE, symTable)
print(symTable)
