import argparse
import time
import sys
import re
import pydot

LOG_FILE = ''
GRAMMAR_FILE = ''
CONNSTRINGS = ['AND', 'OR', 'IMPLIES', 'IFF', 'NOT']
QSTRINGS = ['EXISTS', 'FORALL']
LOOKAHEAD_INDEX = 0
FORM_INDEX = 0
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


def open_logger(path):
    global LOG_FILE
    try:
        LOG_FILE = open(path, 'w')
    except IOError:
        sys.exit('Could not open log file. EXITING.')


def close_logger():
    global LOG_FILE
    try:
        LOG_FILE.close()
    except IOError:
        sys.exit('Could not close log file. EXITING.')


def log_error(err_str):
    print(err_str)
    try:
        LOG_FILE.write(f'[ERROR] {err_str}\n')
        sys.exit()
    except IOError:
        sys.exit('Could not write to log file. EXITING.')


def log_msg(msg_str):
    print(msg_str)
    try:
        LOG_FILE.write(f'[MSG] {msg_str}\n')
    except IOError:
        sys.exit('Could not write to log file. EXITING.')


def open_grammar(path):
    global GRAMMAR_FILE
    try:
        GRAMMAR_FILE = open(path, 'w')
    except IOError:
        sys.exit('Could not open log file. EXITING.')


def close_grammar():
    global GRAMMAR_FILE
    try:
        GRAMMAR_FILE.close()
    except IOError:
        sys.exit('Could not close log file. EXITING.')


def log_grammar(msg_str):
    print(msg_str)
    try:
        GRAMMAR_FILE.write(f'{msg_str}\n')
    except IOError:
        sys.exit('Could not write to log file. EXITING.')


def escape_bslash(string):
    return string.replace('\\', '\\\\')


def validate_var(var, var_type):
    if not re.fullmatch(r'[a-zA-Z0-9_]+', var):
        log_error(f'{var_type} {var} contains an invalid symbol. {var_type}s' +
                  f' can only contain alphanumeric characters or underscores')


def validate_quant_conn(var, var_type):
    if not re.fullmatch(r'[a-zA-Z0-9_\\]+', var):
        log_error(f'{var_type} {var} contains an invalid symbol. {var_type}s' +
                  f' can only contain alphanumeric characters, underscores' +
                  f' or backslashes')


def validate_equality(var):
    if not re.fullmatch(r'[a-zA-Z0-9_=\\]+', var):
        log_error(f'Equality {var} contains an invalid symbol. Equality' +
                  f' can only contain alphanumeric characters, underscores' +
                  f' or "="')


def parse_variables(line_split, sym_table):
    if len(line_split) == 2:
        variables = line_split[1].split()
        for var in variables:
            validate_var(var, 'Variable')
            if var in sym_table:
                log_error(
                    f'Variable {var} is already defined as a' +
                    f' {sym_table[var][0]}')
            else:
                sym_table[var] = ['VARIABLE']


def parse_constants(line_split, sym_table):
    if len(line_split) == 2:
        constants = line_split[1].split()
        for con in constants:
            validate_var(con, 'Constant')
            if con in sym_table:
                log_error(
                    f'Constant {con} is already defined as a' +
                    f' {sym_table[con][0]}')
            else:
                sym_table[con] = ['CONSTANT']


def parse_equality(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 1:
        log_error(
            'Exactly 1 equality symbol must be sepecified in an' +
            f' input file')
    equality = line_split[1].split()[0]
    validate_equality(equality)
    if equality in sym_table:
        log_error(
            f'Equality {equality} is already defined as a' +
            f' {sym_table[equality][0]}')
    else:
        sym_table[equality] = ['EQUALITY']


def parse_connectives(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 5:
        log_error('Exactly 5 equality symbols must be defined')
    connectives = line_split[1].split()
    count = 0
    for con in connectives:
        validate_quant_conn(con, 'Connective')
        if con in sym_table:
            log_error(
                f'Connective {con} is already defined as a' +
                f' {sym_table[con][0]}')
        else:
            sym_table[con] = ['CONNECTIVE', CONNSTRINGS[count]]
            count += 1


def parse_quantifiers(line_split, sym_table):
    if len(line_split) != 2 or len(line_split[1].split()) != 2:
        log_error('Exactly 2 quantifiers must be sepecified')
    quantifiers = line_split[1].split()
    count = 0
    for quant in quantifiers:
        validate_quant_conn(quant, 'Quantifier')
        if quant in sym_table:
            log_error(
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
                log_error(
                    f'Predicate {pred} does not match valid predicate' +
                    f' syntax. Correct syntax is symbol[count]')
            name = re.match(r'[a-zA-Z0-9_]+', pred).group(0)
            count = pred.split('[')[1][0:-1]
            if name in sym_table:
                log_error(
                    f'Predicate {name} is already defined as a' +
                    f' {sym_table[name][0]}')
            else:
                sym_table[name] = ['PREDICATE', count]


def parse_formula(lines, count):
    global FORMULA
    skip = 0
    split = lines[count].split(':')
    if len(split) != 2:
        log_error('You must specify a formula in the input file')
    FORMULA = ' '.join(split[1].split()).strip()
    if len(FORMULA) == 0:
        log_error('You must specify a formula in the input file')
    for i in range(count + 1, len(lines)):
        if len(lines[i].split(':')) == 1:
            FORMULA += ' '.join(lines[i].split()).strip()
            skip += 1
        else:
            break
    return skip


def read_in_file(file_name, sym_table):
    try:
        with open(file_name) as in_file:
            lines = list(in_file)
    except IOError:
        log_error('Could not open input file.')
    i = 0
    var = (False, 0)
    con = (False, 0)
    eq = (False, 0)
    conn = (False, 0)
    quant = (False, 0)
    pred = (False, 0)
    form = (False, 0)
    while i < len(lines):
        line = lines[i]
        line_split = line.split(':')
        if line_split[0].strip() == 'variables':
            if var[0]:
                log_error(f'Variables have already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg(f'Reading Variables')
            parse_variables(line_split, sym_table)
            var = (True, i)
        elif line_split[0].strip() == 'constants':
            if con[0]:
                log_error(f'Constants have already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg(f'Reading Constants')
            parse_constants(line_split, sym_table)
            con = (True, i)
        elif line_split[0].strip() == 'equality':
            if eq[0]:
                log_error(f'Equality has already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg(f'Reading Equality')
            parse_equality(line_split, sym_table)
            eq = (True, i)
        elif line_split[0].strip() == 'connectives':
            if conn[0]:
                log_error(f'Connectives have already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg(f'Reading Connectives')
            parse_connectives(line_split, sym_table)
            conn = (True, i)
        elif line_split[0].strip() == 'quantifiers':
            if quant[0]:
                log_error(f'Quantifiers have already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg('Reading Quantifiers')
            parse_quantifiers(line_split, sym_table)
            quant = (True, i)
        elif line_split[0].strip() == 'predicates':
            if pred[0]:
                log_error(f'Predicates have already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg('Reading Predicates')
            parse_predicates(line_split, sym_table)
            pred = (True, i)
        elif line_split[0].strip() == 'formula':
            if form[0]:
                log_error(f'Formula has already been defined' +
                          f' on line {var[1]} of input file' +
                          f' cannot redefine them on line {i}')
            log_msg('Reading Formula')
            skip = parse_formula(lines, i)
            form = (True, i)
            i += skip
        else:
            log_error(f'Invalid field name {line_split[0].strip()} on' +
                      f' line {i}')
        i += 1


def print_terminals():
    log_grammar('Terminal symbols:')
    syms = ''
    if VARIABLES:
        syms += f'{" ".join(VARIABLES)}'
        syms += ' '
    if CONSTANTS:
        syms += f'{" ".join(CONSTANTS)}'
        syms += ' '
    if QUANTIFIERS:
        syms += f'{" ".join(QUANTIFIERS)}'
        syms += ' '
    if CONNECTIVES:
        syms += f'{" ".join(CONNECTIVES)}'
        syms += ' '
    if NEGATION:
        syms += f'{NEGATION} '
    if EQUALITY:
        syms += f'{EQUALITY} '
    if PREDICATES:
        syms += f'{" ".join(PREDICATES)}'
        syms += ' '
    syms += '( ) ,'
    log_grammar(syms)


def print_non_terminals():
    log_grammar('Non-terminal symbols:')
    syms = ''
    syms += "<Constant> <Variable> "
    for pred in PREDICATES:
        syms += f"<{pred}_rule> "
    syms += ("<Predicate_rule> <Equality> <Quantifier > " +
             "<Connective> <Negation> <Atom> <Formula>")
    log_grammar(syms)


def print_constants():
    msg_str = ''
    msg_str += '<Constant> -> '
    if not CONSTANTS:
        log_grammar(msg_str)
        return
    msg_str += f'{"|".join(CONSTANTS)}'
    log_grammar(msg_str)


def print_variables():
    msg_str = ''
    msg_str += '<Variable> -> '
    if not CONSTANTS:
        log_grammar(msg_str)
        return
    msg_str += f'{"|".join(VARIABLES)}'
    log_grammar(msg_str)


def print_predicates(sym_table):
    msg_str = ''
    if not PREDICATES:
        log_grammar('')
        return
    for pred in PREDICATES:
        msg_str = ''
        msg_str += f'<{pred}_rule> -> {pred}('
        for _ in range(int(sym_table[pred][1])-1):
            msg_str += '<Variable>,'
        msg_str += '<Variable>)'
        log_grammar(msg_str)
    msg_str = '<Predicate_rule> -> '
    for i in range(len(PREDICATES)-1):
        msg_str += f'<{PREDICATES[i]}_rule>|'
    msg_str += f'<{PREDICATES[-1]}_rule>'
    log_grammar(msg_str)


def print_quantifiers():
    msg_str = ''
    msg_str += '<Quantifier> -> '
    msg_str += f'{"|".join(QUANTIFIERS)}'
    log_grammar(msg_str)


def print_connectives():
    msg_str = ''
    msg_str += '<Connective> -> '
    msg_str += f'{"|".join(CONNECTIVES)}'
    log_grammar(msg_str)


def print_formulae():
    log_grammar('<Atom> -> <Predicate_rule>|(<Constant><Equality>' +
                '<Constant>)|(<Constant><Equality><Variable>)|(' +
                '<Variable><Equality><Constant>)|(<Variable>' +
                '<Equality><Variable>)')
    log_grammar('<Formula> -> <Atom>|(<Formula><Connective><Formula>)|' +
                '<Negation><Formula>|<Quantifier><Formula>')


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
    time_str = time.strftime('%Y-%m-%d_%H-%M-%S')
    log_msg(f'Opening grammar output file at {time_str}_' +
            f'{GRAMMAR_FILE_NAME}.txt')
    open_grammar(f'{time_str}_{GRAMMAR_FILE_NAME}.txt')
    log_msg('Writing grammar to grammar output file')
    log_grammar('Grammar for first order logic formula')
    print_terminals()
    print_non_terminals()
    log_grammar('Production rules for the first order logic language.')
    print_constants()
    print_variables()
    print_predicates(sym_table)
    log_grammar('<Equality> -> ' + EQUALITY)
    print_quantifiers()
    print_connectives()
    log_grammar('<Negation> -> ' + NEGATION)
    print_formulae()
    log_msg('Closing grammar output file')
    close_grammar()


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
    leading_space = 0
    while i < len(FORMULA):
        if FORMULA[i] == '(':
            TOKENS.append(['(', '(', leading_space])
            leading_space = 0
            i += 1
        elif FORMULA[i] == ')':
            TOKENS.append([')', ')', leading_space])
            leading_space = 0
            i += 1
        elif FORMULA[i] == ',':
            TOKENS.append([',', ',', leading_space])
            leading_space = 0
            i += 1
        elif FORMULA[i].isspace():
            leading_space += 1
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
                log_error('Formula contains invalid identifiers')
            else:
                TOKENS.append(
                    [candidates[0][1], candidates[0][0], leading_space])
                leading_space = 0
                i += len(candidates[0][0])


def add_tree(graph, label, parent_id):
    global NODE_ID
    if (label in ('Quantifier', 'Connective', 'Variable',
                  'Constant', 'Negation', 'Equality')):
        graph.add_node(pydot.Node(NODE_ID, label=f'"<{label}>"'))
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX-1][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
    elif label == 'Predicate':
        graph.add_node(pydot.Node(NODE_ID, label=f'"<{label}>"'))
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"<{escape_bslash(TOKENS[LOOKAHEAD_INDEX-1][1])}' +
            f'_rule>"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        NODE_ID += 1
        graph.add_node(pydot.Node(
            NODE_ID, label=f'"{escape_bslash(TOKENS[LOOKAHEAD_INDEX-1][1])}"'))
        graph.add_edge(pydot.Edge(NODE_ID-1, NODE_ID))
        TERM_NODES.append(NODE_ID)
        NODE_ID += 1
    elif label == 'Formula':
        graph.add_node(pydot.Node(NODE_ID, label=f'"<{label}>"'))
        if parent_id > -1:
            graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1
    else:
        graph.add_node(pydot.Node(NODE_ID, label=f'"{escape_bslash(label)}"'))
        graph.add_edge(pydot.Edge(parent_id, NODE_ID))
        NODE_ID += 1


def match(terminal):
    global LOOKAHEAD_INDEX, FORM_INDEX
    if LOOKAHEAD_INDEX == len(TOKENS):
        log_error(f'Syntax Error. Expected {terminal} at formula position' +
                  f' {FORM_INDEX}. Instead found nothing.')
    if terminal == TOKENS[LOOKAHEAD_INDEX][0]:
        FORM_INDEX += len(TOKENS[LOOKAHEAD_INDEX][1])
        if LOOKAHEAD_INDEX < len(TOKENS) - 1:
            FORM_INDEX += TOKENS[LOOKAHEAD_INDEX+1][2]
        LOOKAHEAD_INDEX += 1
    else:
        log_error(f'Syntax Error. Expected {terminal} at formula position ' +
                  f'{FORM_INDEX} instead found' +
                  f' {TOKENS[LOOKAHEAD_INDEX][1]}')


def predicate_rule(sym_table, graph, parent_id):
    global NODE_ID
    if LOOKAHEAD_INDEX == len(TOKENS):
        log_error(f'Syntax Error. Expected Predicate at formula position ' +
                  f'{FORM_INDEX}. Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        count = int(sym_table[TOKENS[LOOKAHEAD_INDEX][1]][1])
        match('PREDICATE')
        add_tree(graph, 'Predicate', parent_id)
        TERM_NODES.append(NODE_ID-1)
        start_id = NODE_ID - 2
        match('(')
        add_tree(graph, '(', start_id)
        TERM_NODES.append(NODE_ID-1)
        for _ in range(count-1):
            match('VARIABLE')
            add_tree(graph, 'Variable', start_id)
            TERM_NODES.append(NODE_ID-1)
            match(',')
            add_tree(graph, ',', start_id)
            TERM_NODES.append(NODE_ID-1)
        match('VARIABLE')
        add_tree(graph, 'Variable', start_id)
        TERM_NODES.append(NODE_ID-1)
        match(')')
        add_tree(graph, ')', start_id)
        TERM_NODES.append(NODE_ID-1)
    else:
        log_error(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX][1]}' +
                  f' in Predicate found at formula position {FORM_INDEX}' +
                  f' expected Predicate')


def const_var(graph, parent_id):
    global NODE_ID
    if LOOKAHEAD_INDEX == len(TOKENS):
        log_error(f'Syntax Error. Expected Variable or Constant at ' +
                  f'formula position {FORM_INDEX}. Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == 'CONSTANT':
        match('CONSTANT')
        add_tree(graph, 'Constant', parent_id)
        TERM_NODES.append(NODE_ID-1)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'VARIABLE':
        match('VARIABLE')
        add_tree(graph, 'Variable', parent_id)
        TERM_NODES.append(NODE_ID-1)
    else:
        log_error(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX][1]}' +
                  f' in Atom at formula position {FORM_INDEX} expected ' +
                  f'Variable or Constant')


def atom(sym_table, graph, parent_id):
    global NODE_ID, TERM_NODES
    add_tree(graph, '<Atom>', parent_id)
    start_id = NODE_ID - 1
    if LOOKAHEAD_INDEX == len(TOKENS):
        log_error(f'Syntax Error. Expected Atom at formula position {FORM_INDEX}.' +
                  f' Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == '(':
        match('(')
        add_tree(graph, '(', start_id)
        TERM_NODES.append(NODE_ID-1)
        const_var(graph, start_id)
        match('EQUALITY')
        add_tree(graph, 'Equality', start_id)
        TERM_NODES.append(NODE_ID-1)
        const_var(graph, start_id)
        match(')')
        add_tree(graph, ')', start_id)
        TERM_NODES.append(NODE_ID-1)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        predicate_rule(sym_table, graph, start_id)
    else:
        log_error(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX][1]}' +
                  f' in Atom at formula position {FORM_INDEX} expected ' +
                  f'( or Predicate')


def formula(sym_table, graph, parent_id):
    global NODE_ID
    add_tree(graph, 'Formula', parent_id)
    start_id = NODE_ID - 1
    if LOOKAHEAD_INDEX == len(TOKENS):
        log_error(f'Syntax Error. Expected Formula at formula position ' +
                  f'{FORM_INDEX}. Instead found nothing.')
    if TOKENS[LOOKAHEAD_INDEX][0] == '(':
        if (LOOKAHEAD_INDEX < len(TOKENS)-1 and
                (TOKENS[LOOKAHEAD_INDEX+1][0] in ('VARIABLE', 'CONSTANT'))):
            atom(sym_table, graph, start_id)
        else:
            match('(')
            add_tree(graph, '(', start_id)
            TERM_NODES.append(NODE_ID-1)
            formula(sym_table, graph, start_id)
            match('CONNECTIVE')
            add_tree(graph, 'Connective', start_id)
            TERM_NODES.append(NODE_ID-1)
            formula(sym_table, graph, start_id)
            match(')')
            add_tree(graph, ')', start_id)
            TERM_NODES.append(NODE_ID-1)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'NEGATION':
        match('NEGATION')
        add_tree(graph, 'Negation', start_id)
        TERM_NODES.append(NODE_ID-1)
        formula(sym_table, graph, start_id)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'QUANTIFIER':
        match('QUANTIFIER')
        add_tree(graph, 'Quantifier', start_id)
        TERM_NODES.append(NODE_ID-1)
        match('VARIABLE')
        add_tree(graph, 'Variable', start_id)
        TERM_NODES.append(NODE_ID-1)
        formula(sym_table, graph, start_id)
    elif TOKENS[LOOKAHEAD_INDEX][0] == 'PREDICATE':
        atom(sym_table, graph, start_id)
    else:
        log_error(f'Syntax Error. Illegal symbol {TOKENS[LOOKAHEAD_INDEX][1]}' +
                  f' in Formula at formula position {FORM_INDEX} expected ' +
                  f'( or Negation or Quantifier or PREDICATE')
    return True


LOG_FILE_NAME = 'log'
GRAMMAR_FILE_NAME = 'grammar'
PARSE_TREE_NAME = 'parse_tree'

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-l', '--log', nargs=1, metavar='FILE_NAME',
                    dest='log_file', help='Filename to write log to')
PARSER.add_argument('-t', '--tree', nargs=1, metavar='FILE_NAME',
                    dest='tree_file', help='Filename to write parse tree to')
PARSER.add_argument('-p', '--parse', nargs=1, metavar='FILE_NAME',
                    dest='grammar_file', help='Filename to write grammar to')
PARSER.add_argument('input_file', nargs=1,
                    metavar='FILE', help='File to parse')
OPTIONS = PARSER.parse_args()
if OPTIONS.log_file:
    LOG_FILE_NAME = OPTIONS.log_file[0]
if OPTIONS.tree_file:
    PARSE_TREE_NAME = OPTIONS.tree_file[0]
if OPTIONS.grammar_file:
    GRAMMAR_FILE_NAME = OPTIONS.grammar_file[0]
SYM_TABLE = {'(': ['SEPARATOR', 'OB'], ')': [
    'SEPARATOR', 'CB'], ',': ['SEPARATOR', 'C']}
SYM_TABLE.update({'[': ['FORBIDDEN'], ']': ['FORBIDDEN']})
INFILE = OPTIONS.input_file[0]
TIME_STR = time.strftime('%Y-%m-%d_%H-%M-%S')
open_logger(f'{TIME_STR}_{LOG_FILE_NAME}.txt')
log_msg(f'Created logfile called {TIME_STR}_{LOG_FILE_NAME}.txt')
log_msg(f'Starting read in file {INFILE}')
read_in_file(INFILE, SYM_TABLE)
log_msg(f'Finished Reading in file. Input file was valid')
log_msg(f'Formula used for error messages: {FORMULA}')
log_msg(f'Starting grammar generation')
generate_grammar_lists(SYM_TABLE)
log_msg(f'Finished grammar generation')
log_msg(f'Starting Lexical Analysis')
lex_analysis()
log_msg(f'Finished Lexical Analysis')
PGRAPH = pydot.Dot(graph_type='graph', rankdir='TB')
log_msg(f'Starting parsing')
formula(SYM_TABLE, PGRAPH, -1)
log_msg(f'Finished parsing')
if LOOKAHEAD_INDEX != len(TOKENS):
    log_error(f'Syntax error. Formula is valid until position {FORM_INDEX}.' +
              f' Trailing symbols occur after this. Consider adding brackets' +
              f' around formula position 0 to {FORM_INDEX} and re running' +
              f' compiler.')
log_msg(f'Formula is valid')
subgraph = pydot.Subgraph(rank='max')
for node in TERM_NODES:
    subgraph.add_node(pydot.Node(node))
PGRAPH.add_subgraph(subgraph)
log_msg(f'Saving parse tree to file: {TIME_STR}_{PARSE_TREE_NAME}.png')
PGRAPH.write_png(f'{TIME_STR}_{PARSE_TREE_NAME}.png')
