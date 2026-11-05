from sys import argv

from lexer import lexer
from parser import parser


def compilador(arquivo_codigo: str):
    with open(arquivo_codigo, 'r') as f:
        codigo = f.read()
    
    x = parser.parse(codigo, lexer=lexer)
    print(x)
    



if __name__ == "__main__":
    compilador(argv[1])