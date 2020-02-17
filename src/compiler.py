import sys

CONNSTRINGS = ['AND', 'OR', 'IMPLIES', 'IFF', 'NOT']
QSTRINGS = ['EXISTS', 'FORALL']


def parse_variables(line_split, sym_table):
    if len(line_split) == 2:
        variables = line_split[1].split()
        for var in variables:
            if var in sym_table:
                sys.exit(
                    f'Variable {var} is already defined as a',
                    ' {sym''Table[v][0]}')
            else:
                sym_table[var] = ['VARIABLE']


def parse_constants(line_split, sym_table):
    if len(line_split) == 2:
        constants = line_split[1].split()
        for con in constants:
            if con in sym_table:
                sys.exit(
                    f'Constant {con} is already defined as a',
                    ' {symTable[c][0]}')
            else:
                sym_table[con] = ['CONSTANT']


def parse_equality(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 1:
        sys.exit(
            'Exactly 1 equality symbol must be sepecified in an',
            ' input file')
    equality = line_split[1].split()[0]
    if equality in sym_table:
        sys.exit(
            f'Equality {equality} is already defined as a',
            ' {sym_table[equality][0]}')
    else:
        sym_table[equality] = ['EQUALITY']


def parse_connectives(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 5:
        sys.exit('Exactly 5 equality symbols must be defined')
    connectives = line_split[1].split()
    count = 0
    for con in connectives:
        if con in sym_table:
            sys.exit(
                f'Connective {con} is already defined as a',
                ' {sym_table[con][0]}')
        else:
            sym_table[con] = ['CONNECTIVE', CONNSTRINGS[count]]
            count += 1


def parse_quantifiers(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 2:
        sys.exit('Exactly 2 quantifiers must be sepecified')
    quantifiers = line_split[1].split()
    count = 0
    for quant in quantifiers:
        if quant in sym_table:
            sys.exit(
                f'Quantifier {quant} is already defined as a',
                ' {sym_table[quant][0]}')
        else:
            sym_table[quant] = ['QUANTIFIER', QSTRINGS[count]]
            count += 1


def read_in_file(file_name, sym_table):
    try:
        with open(file_name) as in_file:
            lines = list(in_file)
    except IOError:
        sys.exit('Could not open input file.')
    for line in lines:
        line_split = line.split(':')
        if line_split[0].strip() == 'variables':
            parse_variables(line_split, sym_table)
        elif line_split[0].strip() == 'constants':
            parse_constants(line_split, sym_table)
        elif line_split[0].strip() == 'equality':
            parse_equality(line_split, sym_table)
        elif line_split[0].strip() == 'connectives':
            parse_connectives(line_split, sym_table)
        elif line_split[0].strip() == 'quantifiers':
            parse_quantifiers(line_split, sym_table)


if len(sys.argv) < 2:
    sys.exit('no input file specified')
SYM_TABLE = {'(': ['SEPARATOR', 'OB'], ')': [
    'SEPARATOR', 'CB'], ',': ['SEPARATOR', 'C']}
INFILE = sys.argv[1]
read_in_file(INFILE, SYM_TABLE)
print(SYM_TABLE)
