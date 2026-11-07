from collections import ChainMap
from dataclasses import dataclass
from typing import Literal

from AST import *
from excecao import CompiladorError
from visitador import Visitador


class ErroSemantico(CompiladorError): ...

@dataclass
class Simbolo:
    id: Id

@dataclass
class SimboloPrograma(Simbolo): ...

@dataclass
class SimboloFuncao(Simbolo):
    tipo: TipoRetorno
    params: list[...]

@dataclass
class SimboloVariavel(Simbolo):
    tipo: Tipo
    definida: bool = False

@dataclass
class SimboloParametro(Simbolo):
    tipo: Tipo


def processa_params(params: list[Param]) -> list:
    return [no.tipo for no in params]

class TabelaDeSimbolos(ChainMap):
    def __init__(self):
        super().__init__()

    def salvar(self, s: Simbolo):
        if str(s.id) in self.maps[0]:
            raise ErroSemantico(f"Identificador {name} já declarado anteriormente")
        
        self[s.id] = s

    def entrar_escopo(self):
        novo_escopo = self.new_child()
        self.maps = novo_escopo

    def sair_escopo(self):
        novo_escopo = self.parents 
        self.maps = novo_escopo

    def __missing__(self, key):
        return None

class AnalisadorSemantico(Visitador):
    def __init__(self):
        self.tabela_simbolos = TabelaDeSimbolos()
        self.erros = []

    def visita_Program(self, no: Program):
        s = SimboloPrograma(no.id)
        no.simbolo = s
        self.tabela_simbolos.salvar(s)
        
        for decVar in no.decVariaveis:
            self.visita(decVar)
        for decFun in no.decFuncoes:
            self.visita(decFun)
        for cmd in no.comandos:
            self.visita(cmd)
    
    def visita_DeclaraFuncao(self, no: DeclaraFuncao):
        tipo_params = processa_params(no.params)
        s = SimboloFuncao(no.id, tipo_params)
        no.simbolo = s

        self.tabela_simbolos.salvar(s)
        self.tabela_simbolos.entrar_escopo()

        for param in no.params:
            self.visita(param)
        for decVar in no.decVariaveis:
            self.visita(decVar)
        for decFun in no.decFuncoes:
            self.visita(decFun)
        for cmd in no.comandos:
            self.visita(cmd)

        self.tabela_simbolos.sair_escopo()
    
    def visita_Param(self, no: Param):
        s = SimboloParametro(no.id)
        self.tabela_simbolos.salvar(s)
        no.simbolo = s
        # da pra adicionar erro aqui se tiver 2 param com mesmo nome

    def visita_DeclaraVariavel(self, no: DeclaraVariavel):
        s = SimboloVariavel(no.id, no.tipo)
        self.tabela_simbolos.salvar(s)
        no.simbolo = s

        if no.expr is not None:
            self.visita(no.expr)
            if no.expr.tipo != no.tipo:
                raise ErroSemantico(
                    f"tipo imcompativel: variavel do tipo '{no.tipo}'"
                    f" tentando ser atribuida com tipo '{no.expr.tipo}'")
            s.definida = True

    def visita_CmdAtribuicao(self, no: CmdAtribuicao):
        s = self.tabela_simbolos[no.id]
        if s is None:
            raise ErroSemantico(f"Identificador '{no.id}' não declarado")
        
        no.simbolo_id = s
        
        if type(s) not in (SimboloVariavel, SimboloParametro):
            raise ErroSemantico(f"Identificador '{no.id}' não atribuível")
        
        self.visita(no.expr)

        if s.tipo != no.expr.tipo:
            raise ErroSemantico(
                f"tipo imcompativel: variavel do tipo '{no.tipo}'"
                f" tentando ser atribuida com tipo '{no.expr.tipo}'")

    def visita_CmdRepeticao(self, no: CmdRepeticao):
        self.visita(no.expr)
        tipo_expr = no.expr.tipo

        if tipo_expr != BOOL:
            raise ErroSemantico("Tipo imcompatível: 'while' espera uma expressão booleana válida")

        for cmd in no.bloco:
            self.visita(cmd)
        

    def visita_CmdRetorno(self, no: CmdRetorno):
        pass
    
    def visita_CmdLeitura(self, no: CmdLeitura):
        for id in no.ids:
            self.visita(id)

    def visita_CmdEscrita(self, no: CmdEscrita):
        for expr in no.exprs:
            self.visita(expr)

    def visita_CmdChamada(self, no: CmdChamada):
        pass
    
    def visita_OpAritmetica(self, no: OpAritmetica):
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != INT or tipoEsq != INT:
            raise ErroSemantico(f"Operacao Aritmetica '{no.op}' nao aceita tipo diferente de '{INT}'")

        no.tipo = INT

    def visita_OpRelacional(self, no: OpRelacional):
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != INT or tipoEsq != INT:
            raise ErroSemantico(f"Operacao Relacional '{no.op}' nao aceita tipo diferente de '{INT}'")

        no.tipo = BOOL
    
    def visita_OpIgualdade(self, no: OpIgualdade):
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != tipoEsq:
            raise ErroSemantico(f"Operacao '{no.op}' não aceita tipos diferentes")

        no.tipo = BOOL
    
    def visita_OpLogica(self, no: OpLogica):
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != BOOL or tipoEsq != BOOL:
            raise ErroSemantico(f"Operacao Logica '{no.op}' nao aceita tipo diferente de '{BOOL}'")

        no.tipo = BOOL
    
    def visita_OpUn(self, no: OpUn):
        self.visita(no.expr)

        tipo = no.expr.tipo

        valido = (tipo == INT and no.op == '-') or (tipo == BOOL and no.op == '!')
        if not valido:
            raise ErroSemantico(f"Operacao Unária '{no.op}' nao aceita tipo diferente de '{tipo}'")

        no.tipo = tipo
        
    def visita_Id(self, no: Id):
        s = self.tabela_simbolos[no]
        
        no.simbolo = s
        no.tipo = s.tipo

    def visita_Numero(self, no: Numero):
        no.tipo = "int"
    
    def visita_Booleano(self, no: Booleano):
        no.tipo = "bool"

    def visita_Chamada(self, no: Chamada):
        ...
        

