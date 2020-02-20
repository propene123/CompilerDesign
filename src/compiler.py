import sys
import re

CONNSTRINGS = ['AND', 'OR', 'IMPLIES', 'IFF', 'NOT']
QSTRINGS = ['EXISTS', 'FORALL']
LOOKAHEAD = ''
EQUALITY = ''
NEGATION = ''
CONNECTIVES = []
QUANTIFIERS = []
VARIABLES = []
CONSTANTS = []
PREDICATES = []


def validate_var(var):
    if not re.fullmatch(r'[a-zA-Z0-9_]', var):
        sys.exit(f'Identifier {var} contains an invalid symbol. Identifiers' +
                 f' can only contain alphanumeric characters or underscores')


def parse_variables(line_split, sym_table):
    if len(line_split) == 2:
        variables = line_split[1].split()
        for var in variables:
            validate_var(var)
            if var in sym_table:
                sys.exit(
                    f'Variable {var} is already defined as a' +
                    f' {sym_table[var][0]}')
            else:
                sym_table[var] = ['VARIABLE']


def parse_constants(line_split, sym_table):
    if len(line_split) == 2:
        constants = line_split[1].split()
        for con in constants:
            validate_var(con)
            if con in sym_table:
                sys.exit(
                    f'Constant {con} is already defined as a' +
                    f' {sym_table[con][0]}')
            else:
                sym_table[con] = ['CONSTANT']


def parse_equality(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 1:
        sys.exit(
            'Exactly 1 equality symbol must be sepecified in an' +
            f' input file')
    equality = line_split[1].split()[0]
    if equality in sym_table:
        sys.exit(
            f'Equality {equality} is already defined as a' +
            f' {sym_table[equality][0]}')
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
                f'Connective {con} is already defined as a' +
                f' {sym_table[con][0]}')
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
                f'Quantifier {quant} is already defined as a' +
                f' {sym_table[quant][0]}')
        else:
            sym_table[quant] = ['QUANTIFIER', QSTRINGS[count]]
            count += 1


def parse_predicates(line_split, sym_table):
    if len(line_split) == 2:
        predicates = line_split[1].split()
        for pred in predicates:
            if not re.fullmatch(r'[a-zA-Z0-9_]+\[[0-9]+\]', pred):
                sys.exit(
                    f'Predicate {pred} does not match valid predicate' +
                    f' syntax. Correct syntax is symbol[count]')
            name = re.match(r'[a-zA-Z0-9_]+', pred).group(0)
            count = pred.split('[')[1][0:-1]
            if name in sym_table:
                sys.exit(
                    f'Predicate {name} is already defined as a' +
                    f' {sym_table[name][0]}')
            else:
                sym_table[name] = ['PREDICATE', count]


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
        elif line_split[0].strip() == 'predicates':
            parse_predicates(line_split, sym_table)


def print_constants():
    print('Constant -> ', end='')
    for i in range(len(CONSTANTS)-1):
        print(CONSTANTS[i], end='|')
    print(CONSTANTS[-1])


def print_variables():
    print('Variable -> ', end='')
    for i in range(len(VARIABLES)-1):
        print(VARIABLES[i], end='|')
    print(VARIABLES[-1])


def print_predicates(sym_table):
    for pred in PREDICATES:
        print(f'{pred}_rule -> {pred}(', end='')
        for _ in range(int(sym_table[pred][1])-1):
            print('variable', end=',')
        print('variable)')
    print('Predicate_rule -> ', end='')
    for i in range(len(PREDICATES)-1):
        print(f'{PREDICATES[i]}_rule', end='|')
    print(f'{PREDICATES[-1]}_rule')


def print_quantifiers():
    print('Quantifier -> ', end='')
    for i in range(len(QUANTIFIERS)-1):
        print(QUANTIFIERS[i], end='|')
    print(QUANTIFIERS[-1])


def print_connectives():
    print('Connective -> ', end='')
    for i in range(len(CONNECTIVES)-1):
        print(CONNECTIVES[i], end='|')
    print(CONNECTIVES[-1])


def print_formulae():
    print('Atom -> Predicate_rule|(ConstantEqualityConstant)|' +
          '(ConstantEqualityVariable)|' +
          '(VariableEqualityConstant)|(VariableEqualityVariable)')
    print('Formula -> Atom|(FormulaConnectiveFormula)|' +
          'NegationFormula|QuantifierFormula')


def generate_grammar_lists(sym_table):
    global CONSTANTS, VARIABLES, PREDICATES, EQUALITY, QUANTIFIERS, NEGATION
    for sym, attrib in sym_table.items():
        if attrib[0] == 'CONSTANT':
            CONSTANTS.append(sym)
        elif attrib[0] == 'VARIABLE':
            VARIABLES.append(sym)
        elif attrib[0] == 'PREDICATE':
            PREDICATES.append(sym)
        elif attrib[0] == 'EQUALITY':
            EQUALITY = sym
        elif attrib[0] == 'QUANTIFIER':
            QUANTIFIERS.append(sym)
        elif attrib[0] == 'CONNECTIVE':
            if attrib[1] == 'NOT':
                NEGATION = sym
            else:
                CONNECTIVES.append(sym)
    print('Grammar rules for the first order logic language.')
    print_constants()
    print_variables()
    print_predicates(sym_table)
    print('Equality ->', EQUALITY)
    print_quantifiers()
    print_connectives()
    print('Negation ->', NEGATION)
    print_formulae()


def predicate_rule(sym_table):
    if LOOKAHEAD in PREDICATES:
        count = sym_table[LOOKAHEAD][1]
        match('PREDICATE')
        match('(')
        for i in range(count-1):
            match('VARIABLE')
            match(',')
        match('VARIABLE')
        match(')')


def const_var():
    if LOOKAHEAD in CONSTANTS:
        match('CONSTANT')
    elif LOOKAHEAD in VARIABLES:
        match('VARIABLE')
    else:
        sys.exit('Syntax Error')


def atom(sym_table):
    if LOOKAHEAD == '(':
        match('(')
        const_var()
        match('EQUALITY')
        match(')')
    elif LOOKAHEAD in PREDICATES:
        predicate_rule(sym_table)
    else:
        sys.exit('Syntax Error')


def formula(sym_table):
    if LOOKAHEAD == '(':
        if not atom(sym_table):
            match('(')
            formula()
            match('CONNECTIVE')
            formula()
            match(')')
    elif LOOKAHEAD == NEGATION:
        match('NEGATION')
        formula()
    elif LOOKAHEAD in QUANTIFIERS:
        match('QUANTIFIER')
        formula()
    else:
        sys.exit('Syntax Error')
    return True


if len(sys.argv) < 2:
    sys.exit('no input file specified')
SYM_TABLE = {'(': ['SEPARATOR', 'OB'], ')': [
    'SEPARATOR', 'CB'], ',': ['SEPARATOR', 'C']}
SYM_TABLE.update({'[': ['FORBIDDEN'], ']': ['FORBIDDEN']})
INFILE = sys.argv[1]
read_in_file(INFILE, SYM_TABLE)
generate_grammar_lists(SYM_TABLE)
