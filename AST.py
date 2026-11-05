from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Tipo = Literal['int', 'bool']
TipoRetorno = Literal['int', 'bool', 'void']

@dataclass
class No:
    pass

@dataclass
class Program(No):
    id: Id
    decVariaveis: list[DeclaraVariavel]
    decFuncoes: list[DeclaraFuncao]
    comandos: list[Cmd]

@dataclass
class DeclaraFuncao(No):
    id: Id
    params: list[Param]
    tipoRetorno: TipoRetorno
    decVariaveis: list[DeclaraVariavel]
    decFuncoes: list[DeclaraFuncao]
    comandos: list[Cmd]

@dataclass
class Param(No):
    tipo: Tipo
    id: Id

@dataclass
class DeclaraVariavel(No):
    tipo: Tipo
    id: Id
    expr: Expr | None


@dataclass
class Cmd(No):
    pass

@dataclass
class Atribuicao(Cmd):
    var: Id
    expr: Expr

@dataclass
class Condicional(Cmd):
    expr: Expr
    bloco1: list[Cmd]
    bloco2: list[Cmd] 

@dataclass
class Repeticao(Cmd):
    expr: Expr
    bloco: list[Cmd]

@dataclass
class Retorno(Cmd):
    expr: Expr | None

@dataclass
class Leitura(Cmd):
    ids: list[Id]

@dataclass
class Escrita(Cmd):
    exprs: list[Expr]

@dataclass
class Chamada(No):
    id: Expr
    params: list[Expr]

@dataclass
class ChamadaCmd(Cmd):
    chamada: Chamada

@dataclass
class Expr(No):
    pass

@dataclass
class OpBin(Expr):
    op: Literal['+', '-', '*', '/', '<', '<=', '>', '>=', '==', '!=', '&&', '||']
    ladoEsq: Expr
    ladoDir: Expr

@dataclass
class OpUn(Expr):
    op: Literal['!', '-']
    expr: Expr

@dataclass
class Numero(Expr):
    valor: int

@dataclass
class Booleano(Expr):
    valor: bool

@dataclass
class ChamadaExpr(Expr):
    chamada: Chamada

@dataclass
class Id(No):
    nome: str