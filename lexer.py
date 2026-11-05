from ply.lex import lex

reserved = {
    'program': 'PROGRAM',
    'fun': 'FUN',

    'int': 'INT',
    'bool': 'BOOL',
    'void': 'VOID',

    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',

    'return': 'RETURN',
    'read': 'READ',
    'print': 'PRINT',

    'true': 'TRUE',
    'false': 'FALSE'
}

literals = ['(', ')', ';', '{', '}', ',']

tokens = [
    'ID',

    'ARROW',
    'EQ',
    'NEQ',
    'ASSIGN',

    'LT',
    'LEQ',
    'GT',
    'GEQ',

    'NUMBER',
    'BOOLEAN',
    
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    
    'AND',
    'OR',
    'NOT',
    
    'COMMENT'
] + list(reserved.values())


t_ignore = ' \t'
t_ARROW = '->'
t_EQ = '=='
t_NEQ = '!='
t_ASSIGN = '='
t_LT = '<'
t_LEQ = '<='
t_GT = '>'
t_GEQ = '>='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_OR = r'\|\|'
t_AND = r'&&'
t_NOT = r'!'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'//.*'

def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    if t.value in ("true", "false"):
        t.type = "BOOLEAN"
    else:
        t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_BOOLEAN(t):
    r'(true|false)'
    t.value = (t.value == 'true')
    return t

def t_error(t):
    print(f"Caracter inválido: '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex()
