from AST import *
from lexer import tokens
from ply.yacc import yacc

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LT', 'LEQ', 'GT', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS')
)

def p_programa(p):
    r"programa ::= PROGRAM ID '{' dec_vars dec_funs comandos '}'"
    p[0] = Program(Id(p[2]), p[4], p[5], p[6])

def p_dec_funs_vazio(p):
    r"dec_funs ::= vazio"
    p[0] = []

def p_dec_funs_um(p):
    r"dec_funs ::= dec_fun"
    p[0] = [p[1]]

def p_dec_funs_varios(p):
    r"dec_funs ::= dec_funs dec_fun"
    p[1].append(p[2])
    p[0] = p[1] 

def p_dec_fun(p):
    r"""dec_fun ::= FUN ID '(' params ')' ARROW tipo_retorno '{' dec_vars dec_funs comandos '}' """
    p[0] = DeclaraFuncao(Id(p[2]), p[4], p[7], p[9], p[10], p[11])

def p_params_vazio(p):
    r"params ::= vazio"
    p[0] = []

def p_params_um(p):
    r"params ::= param"
    p[0] = [p[1]]

def p_params_varios(p):
    r"params ::= params ',' param"
    p[1].append(p[3])
    p[0] = p[1]

def p_param(p):
    r"param ::= tipo ID"
    p[0] = Param(p[1], Id(p[2]))

def p_dec_vars_vazio(p):
    r"dec_vars ::= vazio"
    p[0] = []

def p_dec_vars_um(p):
    r"dec_vars ::= dec_var"     
    p[0] = [p[1]]

def p_dec_vars_varios(p):
    r"dec_vars ::= dec_vars dec_var"
    p[1].append(p[2])
    p[0] = p[1]

def p_dec_var(p):
    r"dec_var ::= tipo ID ';'"
    p[0] = DeclaraVariavel(p[1], Id(p[2]), None)

def p_dec_var_and_assign(p):
    r"dec_var ::= tipo ID ASSIGN expr ';'"
    p[0] = DeclaraVariavel(p[1], Id(p[2]), p[4])

def p_tipo(p):
    r"""
    tipo ::= INT 
           | BOOL
    """
    p[0] = str(p[1]).lower() 

def p_tipo_retorno(p):
    r"""
    tipo_retorno ::= INT
                   | BOOL
                   | VOID
    """
    p[0] = str(p[1]).lower()

def p_comandos_vazio(p):
    r"comandos ::= vazio"
    p[0] = []

def p_comandos_um(p):
    r"comandos ::= comando"
    p[0] = [p[1]]

def p_comandos_varios(p):
    r"comandos ::= comandos comando"
    p[1].append(p[2])
    p[0] = p[1]

def p_comando(p):
    r"""
    comando ::= atribuicao
              | condicional
              | repeticao
              | retorno
              | leitura
              | escrita
              | chamada_comando"""
    p[0] = p[1]

def p_atribuicao(p):
    r"atribuicao ::= ID ASSIGN expr ';'"
    p[0] = CmdAtribuicao(Id(p[1]), p[3])

def p_condicional_sem_else(p):
    r"condicional ::= IF '(' expr ')' bloco"
    p[0] = CmdCondicional(p[3], p[5], [])

def p_condicional_com_else(p):
    r"condicional ::= IF '(' expr ')' bloco ELSE bloco"
    p[0] = CmdCondicional(p[3], p[5], p[7])

def p_repeticao(p):
    r"repeticao ::= WHILE '(' expr ')' bloco"
    p[0] = CmdRepeticao(p[3], p[5])

def p_bloco(p):
    r"bloco ::= '{' comandos '}'"
    p[0] = p[1]

def p_retorno_vazio(p):
    r"retorno ::= RETURN ';'"
    p[0] = CmdRetorno(None)

def p_retorno_com_valor(p):
    r"retorno ::= RETURN expr ';'"
    p[0] = CmdRetorno(p[2])

def p_leitura(p):
    r"leitura ::= READ '(' lista_identificadores ')' ';'"
    p[0] = CmdLeitura(p[3])

def p_lista_identificadores_um(p):
    r"lista_identificadores ::= ID"
    p[0] = [Id(p[1])]

def p_lista_identificadores_varios(p):
    r"lista_identificadores ::= lista_identificadores ',' ID"
    p[1].append(Id(p[3]))
    p[0] = p[1]

def p_escrita(p):
    r"escrita ::= PRINT '(' lista_expr ')' ';'"
    p[0] = CmdEscrita(p[3])

def p_lista_expr_um(p):
    r"lista_expr ::= expr"
    p[0] = [p[1]]

def p_lista_expr_varios(p):
    r"lista_expr ::= lista_expr ',' expr"
    p[1].append(p[3])
    p[0] = p[1]

def p_chamada_comando(p):
    r"chamada_comando ::= chamada ';'"
    p[0] = CmdChamada(p[1])

def p_chamada_sem_param(p):
    r"chamada ::= ID '(' ')'"
    p[0] = Chamada(Id(p[1]), [])

def p_chamada_com_param(p):
    r"chamada ::= ID '(' lista_expr ')'"
    p[0] = Chamada(Id(p[1]), p[3])

# def p_expr_binaria(p):
#     r"""
#     expr ::= expr OR expr
#             | expr AND expr
#             | expr EQ expr
#             | expr NEQ expr
#             | expr LT expr
#             | expr LEQ expr
#             | expr GT expr
#             | expr GEQ expr
#             | expr PLUS expr
#             | expr MINUS expr   
#             | expr TIMES expr
#             | expr DIVIDE expr
#     """
#     p[0] = OpBin(p[2], p[1], p[3])

def p_expr_Relacional(p):
    r"""
    expr ::= expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
    """
    p[0] = OpRelacional(p[2], p[1], p[3])

def p_expr_igualdade(p):
    r"""
    expr ::= expr  expr
            | expr NEQ expr
    """
    p[0] = OpIgualdade(p[2], p[1], p[3])

def p_expr_logica(p):
    r"""
    expr ::= expr AND expr
            | expr OR expr
    """
    p[0] = OpLogica(p[2], p[1], p[3])

def p_expr_aritmetica(p):
    r"""
    expr ::= expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
    """
    p[0] = OpAritmetica(p[2], p[1], p[3])

def p_expr_unaria(p):
    r"""
    expr ::= MINUS expr %prec UMINUS
           | NOT expr
    """
    p[0] = OpUn(p[1], p[2])

def p_expr_braces(p):
    r"expr ::= '(' expr ')'"
    p[0] = p[1]

def p_expr_numero(p):
    r"expr ::= NUMBER"
    p[0] = Numero(int(p[1]))

def p_expr_booleano(p):
    r"expr ::= BOOLEAN"
    p[0] = Booleano(p[1] == "true")

def p_expr_id(p):
    r"expr ::= ID"
    p[0] = Id(str(p[1]))

def p_expr_chamada(p):
    r"expr ::= chamada"
    p[0] = p[1]

def p_vazio(p):
    "vazio ::= "

def p_error(t):
    print(t)
    raise Exception

parser = yacc(start="programa")
