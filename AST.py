from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

INT = 'int'
BOOL = 'bool'
VOID = 'void'

Tipo = Literal[INT, BOOL]
TipoRetorno = Literal[INT, BOOL, VOID]

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
class CmdAtribuicao(Cmd):
    id: Id
    expr: Expr

@dataclass
class CmdCondicional(Cmd):
    expr: Expr
    bloco_true: list[Cmd]
    bloco_false: list[Cmd] 

@dataclass
class CmdRepeticao(Cmd):
    expr: Expr
    bloco: list[Cmd]

@dataclass
class CmdRetorno(Cmd):
    expr: Expr | None

@dataclass
class CmdLeitura(Cmd):
    ids: list[Id]

@dataclass
class CmdEscrita(Cmd):
    exprs: list[Expr]

@dataclass
class CmdChamada(Cmd):
    chamada: Chamada

@dataclass
class Expr(No):
    pass

@dataclass
class OpBin(Expr):
    op: Literal[str]
    ladoEsq: Expr
    ladoDir: Expr

@dataclass
class OpAritmetica(OpBin):
    op: Literal['+', '-', '*', '/']

@dataclass
class OpRelacional(OpBin):
    op: Literal['<', '<=', '>', '>=']

@dataclass
class OpIgualdade(OpBin):
    op: Literal['==', '!=']

@dataclass
class OpLogica(OpBin):
    op: Literal['&&', '||']

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
class Chamada(Expr):
    id: Id
    params: list[Expr]

@dataclass
class Id(No):
    nome: str

    def __hash__(self):
        return hash(self.nome)