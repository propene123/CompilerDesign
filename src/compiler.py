import sys
import re
import pydot

CONNSTRINGS = ['AND', 'OR', 'IMPLIES', 'IFF', 'NOT']
QSTRINGS = ['EXISTS', 'FORALL']
LOOKAHEAD_INDEX = 0
EQUALITY = ''
NEGATION = ''
CONNECTIVES = []
QUANTIFIERS = []
VARIABLES = []
CONSTANTS = []
PREDICATES = []
FORMULA = ''
TOKENS = []
NODE_ID = 0
TERM_NODES = []


def escape_bslash(string):
    return string.replace('\\', '\\\\')


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


def parse_formula(lines, count):
    global FORMULA
    split = lines[count].split(':')
    if len(split) != 2:
        sys.exit('You must specify a formula in the input file')
    FORMULA = ''.join(split[1].split())
    if len(FORMULA) == 0:
        sys.exit('You must specify a formula in the input file')
    for i in range(count + 1, len(lines)):
        if len(lines[i].split(':')) == 1:
            FORMULA += ''.join(lines[i].split())
        else:
            break


def read_in_file(file_name, sym_table):
    try:
        with open(file_name) as in_file:
            lines = list(in_file)
    except IOError:
        sys.exit('Could not open input file.')
    count = 0
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
        elif line_split[0].strip() == 'formula':
            parse_formula(lines, count)
        count += 1


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


def match_set(sym_set, index):
    current_match = ''
    for sym in sym_set:
        if FORMULA[index:].find(sym) == 0:
            if len(sym) > len(current_match):
                current_match = sym
    return current_match


def lex_analysis():
    global TOKENS
    i = 0
    while i < len(FORMULA):
        if FORMULA[i] == '(':
            TOKENS.append(['('])
            i += 1
        elif FORMULA[i] == ')':
            TOKENS.append([')'])
            i += 1
        elif FORMULA[i] == ',':
            TOKENS.append([','])
            i += 1
        else:
            candidates = []
            candidates.append([match_set(CONNECTIVES, i), 'CONNECTIVE'])
            candidates.append([match_set(VARIABLES, i), 'VARIABLE'])
            candidates.append([match_set(CONSTANTS, i), 'CONSTANT'])
            candidates.append([match_set(QUANTIFIERS, i), 'QUANTIFIER'])
            candidates.append([match_set(PREDICATES, i), 'PREDICATE'])
            candidates.append([match_set([EQUALITY], i), 'EQUALITY'])
            candidates.append([match_set([NEGATION], i), 'NEGATION'])
            candidates.sort(key=lambda item: len(item[0]), reverse=True)
            if len(candidates[0][0]) == 0:
                sys.exit('Formula contains invalid identifiers')
            else:
                TOKENS.append([candidates[0][1], candidates[0][0]])
                i += len(candidates[0][0])


def match(terminal):
    global LOOKAHEAD_INDEX
    if LOOKAHEAD_INDEX == len(TOKENS):
        sys.exit(f'Syntax Error. Expected {terminal} at pos' +
                 f' {LOOKAHEAD_INDEX}. Instead found nothing.')
    if terminal == TOKENS[LOOKAHEAD_INDEX][0]:
        LOOKAHEAD_INDEX += 1
    else:
        sys.exit(f'Syntax Error. Expected {terminal} at pos ' +
                 f'{LOOKAHEAD_INDEX} instead found' +
                 f' {TOKENS[LOOKAHEAD_INDEX]}')


def predicate_rule(sym_table, graph, parent_id):
    global NODE_ID
    graph.add_node(pydot.Node(NODE_ID, label='Predicate'))
    graph.add_edge(pydot.Edge(parent_id, NODE_ID))
    start_id = NODE_ID
    NODE_ID += 1
    if LOOKAHEAD_INDEX == len(TOKENS):
        sys.exit(f'Syntax Error. Expected Predicate at pos {LOOKAHEAD_INDEX}' +
                 f'. Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        count = int(sym_table[TOKENS[LOOKAHEAD_INDEX][1]][1])
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('PREDICATE')
        graph.add_node(pydot.Node(NODE_ID, label='('))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('(')
        for _ in range(count-1):
            graph.add_node(pydot.Node(NODE_ID, label='Variable'))
            graph.add_edge(pydot.Edge(start_id, NODE_ID))
            NODE_ID += 1
            graph.add_node(pydot.Node(
                NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
            graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
            TERM_NODES.append(NODE_ID)
            NODE_ID += 1
            match('VARIABLE')
            graph.add_node(pydot.Node(NODE_ID, label='\,'))
            graph.add_edge(pydot.Edge(start_id, NODE_ID))
            TERM_NODES.append(NODE_ID)
            NODE_ID += 1
            match(',')
        graph.add_node(pydot.Node(NODE_ID, label='Variable'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('VARIABLE')
        graph.add_node(pydot.Node(NODE_ID, label=')'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match(')')
    else:
        sys.exit(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX]}' +
                 f' in Predicate found at pos {LOOKAHEAD_INDEX}' +
                 f' expected Predicate')


def const_var(graph, parent_id):
    global NODE_ID
    if LOOKAHEAD_INDEX == len(TOKENS):
        sys.exit(f'Syntax Error. Expected Variable or Constant at pos' +
                 f' {LOOKAHEAD_INDEX}. Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == 'CONSTANT':
        graph.add_node(pydot.Node(NODE_ID, label='Constant'))
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('CONSTANT')
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'VARIABLE':
        graph.add_node(pydot.Node(NODE_ID, label='VARIABLE'))
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('VARIABLE')
    else:
        sys.exit(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX]}' +
                 f' in Atom at pos {LOOKAHEAD_INDEX} expected Variable or' +
                 f' Constant')


def atom(sym_table, graph, parent_id):
    global NODE_ID, TERM_NODES
    graph.add_node(pydot.Node(NODE_ID, label='Atom'))
    graph.add_edge(pydot.Edge(parent_id, NODE_ID))
    start_id = NODE_ID
    NODE_ID += 1
    if LOOKAHEAD_INDEX == len(TOKENS):
        sys.exit(f'Syntax Error. Expected Atom at pos {LOOKAHEAD_INDEX}.' +
                 f' Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == '(':
        graph.add_node(pydot.Node(NODE_ID, label='('))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('(')
        const_var(graph, start_id)
        graph.add_node(pydot.Node(NODE_ID, label='Equality'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(EQUALITY)}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('EQUALITY')
        const_var(graph, start_id)
        graph.add_node(pydot.Node(NODE_ID, label=')'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match(')')
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        predicate_rule(sym_table, graph, start_id)
    else:
        sys.exit(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX]}' +
                 f' in Atom at pos {LOOKAHEAD_INDEX} expected ( or Predicate')


def formula(sym_table, graph, parent_id):
    global NODE_ID
    graph.add_node(pydot.Node(NODE_ID, label='Formula'))
    if parent_id > -1:
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
    start_id = NODE_ID
    NODE_ID += 1
    if LOOKAHEAD_INDEX == len(TOKENS):
        sys.exit(f'Syntax Error. Expected Formula at pos {LOOKAHEAD_INDEX}.' +
                 f' Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == '(':
        if LOOKAHEAD_INDEX < len(TOKENS)-1:
            if TOKENS[LOOKAHEAD_INDEX+1][0] == 'VARIABLE':
                atom(sym_table, graph, start_id)
            if TOKENS[LOOKAHEAD_INDEX+1][0] == 'CONSTANT':
                atom(sym_table, graph, start_id)
            else:
                graph.add_node(pydot.Node(NODE_ID, label='('))
                graph.add_edge(pydot.Edge(start_id, NODE_ID))
                TERM_NODES.append(NODE_ID)
                NODE_ID += 1
                match('(')
                formula(sym_table, graph, start_id)
                graph.add_node(pydot.Node(NODE_ID, label='CONNECTIVE'))
                graph.add_edge(pydot.Edge(start_id, NODE_ID))
                NODE_ID += 1
                graph.add_node(pydot.Node(
                    NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
                graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
                TERM_NODES.append(NODE_ID)
                NODE_ID += 1
                match('CONNECTIVE')
                formula(sym_table, graph, start_id)
                graph.add_node(pydot.Node(NODE_ID, label=')'))
                graph.add_edge(pydot.Edge(start_id, NODE_ID))
                TERM_NODES.append(NODE_ID)
                NODE_ID += 1
                match(')')
        else:
            graph.add_node(pydot.Node(NODE_ID, '('))
            graph.add_edge(pydot.Edge(start_id, NODE_ID))
            TERM_NODES.append(NODE_ID)
            NODE_ID += 1
            match('(')
            formula(sym_table, graph, start_id)
            graph.add_node(pydot.Node(NODE_ID, label='Connective'))
            graph.add_edge(pydot.Edge(start_id, NODE_ID))
            NODE_ID += 1
            graph.add_node(pydot.Node(
                NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
            graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
            TERM_NODES.append(NODE_ID)
            NODE_ID += 1
            match('CONNECTIVE')
            formula(sym_table, graph, start_id)
            graph.add_node(pydot.Node(NODE_ID, label=')'))
            graph.add_edge(pydot.Edge(start_id, NODE_ID))
            TERM_NODES.append(NODE_ID)
            NODE_ID += 1
            match(')')
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'NEGATION':
        graph.add_node(pydot.Node(NODE_ID, label='Negation'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('NEGATION')
        formula(sym_table, graph, start_id)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'QUANTIFIER':
        graph.add_node(pydot.Node(NODE_ID, label='Quantifier'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('QUANTIFIER')
        graph.add_node(pydot.Node(NODE_ID, label='Variable'))
        graph.add_edge(pydot.Edge(start_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
        match('VARIABLE')
        formula(sym_table, graph, start_id)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        atom(sym_table, graph, start_id)
    else:
        sys.exit(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX]}' +
                 f' in Formula at pos {LOOKAHEAD_INDEX} expected ( or' +
                 f' Variable or Constant or Negation or Quantifier or' +
                 f' PREDICATE')
    return True


if len(sys.argv) < 2:
    sys.exit('no input file specified')
SYM_TABLE = {'(': ['SEPARATOR', 'OB'], ')': [
    'SEPARATOR', 'CB'], ',': ['SEPARATOR', 'C']}
SYM_TABLE.update({'[': ['FORBIDDEN'], ']': ['FORBIDDEN']})
INFILE = sys.argv[1]
read_in_file(INFILE, SYM_TABLE)
generate_grammar_lists(SYM_TABLE)
lex_analysis()
pgraph = pydot.Dot(graph_type='graph', rankdir='TB')
formula(SYM_TABLE, pgraph, -1)
if LOOKAHEAD_INDEX != len(TOKENS):
    sys.exit('Syntax error trailing symbols at end of formula')
subgraph = pydot.Subgraph(rank='same')
for node in TERM_NODES:
    subgraph.add_node(pydot.Node(node))
pgraph.add_subgraph(subgraph)
pgraph.write_png('parse_tree.png')
