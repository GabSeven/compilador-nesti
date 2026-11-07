from sys import argv

from lexer import lexer
from parser import parser
from semantic import AnalisadorSemantico


def compilador(arquivo_codigo: str):
    with open(arquivo_codigo, 'r') as f:
        codigo = f.read()
    
    ast = parser.parse(codigo, lexer=lexer)
    print(ast)
    AnalisadorSemantico().visita(ast)    
    



if __name__ == "__main__":
    compilador(argv[1])