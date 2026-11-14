from collections import ChainMap
from dataclasses import dataclass, field
from typing import Literal

from AST import *
from excecao import CompiladorError
from visitador import Visitador


class ErroSemantico(CompiladorError): ...

@dataclass
class Simbolo:
    id: Id
    nivel_lexico: int | None = field(default=None, init=False)
    endereco: int | None = field(default=None, init=False)

@dataclass
class SimboloPrograma(Simbolo): ...

@dataclass
class SimboloFuncao(Simbolo):
    tipo: TipoRetorno
    params: tuple[Tipo]

@dataclass
class SimboloVariavel(Simbolo):
    tipo: Tipo
    definida: bool = False

@dataclass
class SimboloParametro(Simbolo):
    tipo: Tipo


def tipo_params(params: list[Param]) -> tuple[Tipo]:
    return tuple(no.tipo for no in params)


class TabelaDeSimbolos(ChainMap):
    def __init__(self, *maps):
        super().__init__(*maps)
        self.endereco = [-1]
        self.nivel_lexico = 0

    def novo_endereco(self) -> int:
        self.endereco[-1] += 1
        return self.endereco[-1]

    def salvar(self, s: Simbolo):
        if str(s.id) in self.maps[0]:
            raise ErroSemantico(f"Identificador {name} já declarado anteriormente")
        
        if type(s) not in (SimboloFuncao, SimboloPrograma):
            s.endereco = self.novo_endereco()
        s.nivel_lexico = self.nivel_lexico

        self[s.id] = s

    def entrar_escopo(self):
        self.maps.insert(0, {})
        
        self.nivel_lexico += 1
        self.endereco.append(-1)

    def sair_escopo(self):
        if len(self.maps) > 1:
            self.maps.pop(0)
        
        self.nivel_lexico -= 1
        self.endereco.pop()

    def __missing__(self, key):
        return None

class AnalisadorSemantico(Visitador):
    def __init__(self):
        self.tabela_simbolos = TabelaDeSimbolos()
        self.erros = []
    def visita_Program(self, no: Program):
        s = SimboloPrograma(id=no.id)
        no.simbolo = s
        self.tabela_simbolos.salvar(s)
        
        for decVar in no.decVariaveis:
            self.visita(decVar)
        for decFun in no.decFuncoes:
            self.visita(decFun)
        for cmd in no.comandos:
            self.visita(cmd)
    
    def visita_DeclaraFuncao(self, no: DeclaraFuncao):
        params = no.params
        tipo = tipo_params(params)
        s = SimboloFuncao(id=no.id, params=tipo, tipo=no.tipoRetorno)
        no.simbolo = s
        self.tabela_simbolos.salvar(s)
        self.tabela_simbolos.entrar_escopo()
        no.nivel_lexico = self.tabela_simbolos.nivel_lexico

        for i, param in enumerate(params, start=-(4+len(params))):
            self.visita(param)
            param.simbolo.endereco = i 

        for decVar in no.decVariaveis:
            self.visita(decVar)
        for decFun in no.decFuncoes:
            self.visita(decFun)
        for cmd in no.comandos:
            self.visita(cmd)
            if type(cmd) is CmdRetorno:
                cmd.numero_variaveis = len(no.decVariaveis)
                if not (
                (cmd.expr is None and no.tipoRetorno == VOID)
                or (cmd.expr is not None and cmd.expr.tipo == no.tipoRetorno)):
                    raise ErroSemantico("Tipo retorno inválido")


        self.tabela_simbolos.sair_escopo()
    
    def visita_Param(self, no: Param):
        s = SimboloParametro(id=no.id, tipo=no.tipo)
        self.tabela_simbolos.salvar(s)
        no.simbolo = s
        # da pra adicionar erro aqui se tiver 2 param com mesmo nome

    def visita_DeclaraVariavel(self, no: DeclaraVariavel):
        s = SimboloVariavel(id=no.id, tipo=no.tipo)
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
        no.nivel_lexico = self.tabela_simbolos.nivel_lexico
        self.visita(no.expr)
    
    def visita_CmdLeitura(self, no: CmdLeitura):
        no.simbolos_params = {}
        for id in no.ids:
            if id in no.simbolos_params:
                raise ErroSemantico("2 parametros com mesmo nome")

            self.visita(id)
            no.simbolos_params[id] = id.simbolo

    def visita_CmdEscrita(self, no: CmdEscrita):
        for expr in no.exprs:
            self.visita(expr)

    def visita_CmdChamada(self, no: CmdChamada):
        self.visita(no.chamada)
        
    def visita_CmdCondicional(self, no: CmdCondicional):
        self.visita(no.expr)

        for cmd in no.bloco_true:
            self.visita(cmd)
        for cmd in no.bloco_false:
            self.visita(cmd)
    
    def visita_OpAritmetica(self, no: OpAritmetica):
        no.tipo = INT
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != INT or tipoEsq != INT:
            raise ErroSemantico(f"Operacao Aritmetica '{no.op}' nao aceita tipo diferente de '{INT}'")


    def visita_OpRelacional(self, no: OpRelacional):
        no.tipo = BOOL
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != INT or tipoEsq != INT:
            raise ErroSemantico(f"Operacao Relacional '{no.op}' nao aceita tipo diferente de '{INT}'")

    
    def visita_OpIgualdade(self, no: OpIgualdade):
        no.tipo = BOOL
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != tipoEsq:
            raise ErroSemantico(f"Operacao '{no.op}' não aceita tipos diferentes")

    
    def visita_OpLogica(self, no: OpLogica):
        no.tipo = BOOL
        self.visita(no.ladoDir)
        self.visita(no.ladoEsq)

        tipoDir = no.ladoDir.tipo
        tipoEsq = no.ladoEsq.tipo

        if tipoDir != BOOL or tipoEsq != BOOL:
            raise ErroSemantico(f"Operacao Logica '{no.op}' nao aceita tipo diferente de '{BOOL}'")

    
    def visita_OpUn(self, no: OpUn):
        no.tipo = tipo
        self.visita(no.expr)

        tipo = no.expr.tipo

        valido = (tipo == INT and no.op == '-') or (tipo == BOOL and no.op == '!')
        if not valido:
            raise ErroSemantico(f"Operacao Unária '{no.op}' nao aceita tipo diferente de '{tipo}'")

        
    def visita_Id(self, no: Id):
        s = self.tabela_simbolos[no]
        
        no.simbolo = s
        no.tipo = s.tipo

    def visita_Numero(self, no: Numero):
        no.tipo = "int"
    
    def visita_Booleano(self, no: Booleano):
        no.tipo = "bool"

    def visita_Chamada(self, no: Chamada):
        s : SimboloFuncao = self.tabela_simbolos[no.id]
        if s is None:
            raise ErroSemantico(f"Funcao '{no.id}' não declarada")
        if type(s) is not SimboloFuncao:
            raise ErroSemantico(f"Identificaor '{no.id}' nao é do tipo funcao")

        for param in no.params:
            self.visita(param)

        tipos_recebidos = tipo_params(no.params)
        tipos_esperados = s.params
        if len(tipos_esperados) != len(tipos_recebidos):
            raise ErroSemantico("Quantidade errada de parametros")
        if tipos_esperados != tipos_recebidos:
            raise ErroSemantico("Tipo errado de parametro")
        
        no.simbolo = s
        no.tipo = s.tipo

        
        

