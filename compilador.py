from sys import argv

from gerador_codigo import GeradorCodigoMEPA
from lexer import lexer
from parser import parser
from semantic import AnalisadorSemantico


def compilador(arquivo_codigo: str):
    with open(arquivo_codigo, 'r') as f:
        codigo = f.read()
    
    ast = parser.parse(codigo, lexer=lexer)
    AnalisadorSemantico().visita(ast)    
    gerador = GeradorCodigoMEPA()
    gerador.visita(ast)
    for line in gerador.codigo:
        print(line)



if __name__ == "__main__":
    compilador(argv[1])