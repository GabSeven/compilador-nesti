from AST import *
from semantic import (
    Simbolo,
    SimboloFuncao,
    SimboloParametro,
    SimboloPrograma,
    SimboloVariavel,
)
from visitador import Visitador


class GeradorCodigoMEPA(Visitador):
    def __init__(self):
        self.codigo = []
        self.contador_rotulos = 0


    def rotulo(self, label: str, instr: str): ...

    def inicia_programa(self, id: Id):
        self.codigo.append(f"{id+":":<8}")

    def visita_Program(self, no: Program):
        self.codigo.append("INPP")

        for decVar in no.decVariaveis:
            self.visita(decVar)
        for decFun in no.decFuncoes:
            self.visita(decFun)
        for cmd in no.comandos:
            self.visita(cmd)

        self.codigo.append("PARA")
        self.codigo.append("FIM")
    
    def visita_DeclaraVariavel(self, no: DeclaraVariavel):
        self.codigo.append("AMEM 1")
        if no.expr is not None:
            self.visita(no.expr)
            s : SimboloVariavel = no.simbolo
            self.codigo.append(f"ARMZ {s.nivel_lexico},{s.endereco}")
    
    def visita_CmdEscrita(self, no: CmdEscrita):
        for expr in no.exprs:
            self.visita(expr)
            self.codigo.append("IMPR")

    def visita_Numero(self, no: Numero):
        self.codigo.append(f"CRCT {no.valor}")

    def visita_Id(self, no: Id):
        s : Simbolo = no.simbolo
        self.codigo.append(f"CRVL {s.nivel_lexico},{s.endereco}")

    def visita_CmdAtribuicao(self, no: CmdAtribuicao):
        s : SimboloVariavel = no.simbolo_id
        self.visita(no.expr)
        self.codigo.append(f"ARMZ {s.nivel_lexico},{s.endereco}")

    def visita_OpAritmetica(self, no: OpAritmetica):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)

        op = {'+': 'SOMA', '-': 'SUBT', '*': 'MULT', '/':'DIVI'}
        self.codigo.append(op[no.op])

    def visita_Booleano(self, no: Booleano):
        self.codigo.append(f"CRCT {"1" if no.valor else "0"}")

    def visita_OpUn(self, no: OpUn):
        self.visita(no.expr)
        self.codigo.append({'-': 'INVR', '!':'NEGA'}[no.op])
    
    def visita_OpLogica(self, no: OpLogica):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        self.codigo.append({'&&':'CONJ', '||':'DISJ'}[no.op])

    def visita_OpRelacional(self, no: OpRelacional):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        op = {'<':'CMME', '>': 'CMMA', '<=':'CMEG', '>=':'CMAG'}
        self.codigo.append(op[no.op])

    def visita_OpIgualdade(self, no: OpIgualdade):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        self.codigo.append({'==':'CMIG', '!=':'CMDG'}[no.op])

    def visita_CmdCondicional(self, no: CmdCondicional):
        self.visita(no.expr)
        
        possui_else = len(no.bloco_false) > 0

        self.codigo.append(f"DSVF {"Else" if possui_else else "FimCond"}{self.contador_rotulos}")

        self.codigo.append(f"If{self.contador_rotulos}: NADA")
        for cmd in no.bloco_true:
            self.visita(cmd)
        self.codigo.append(f"DSVS FimCond{self.contador_rotulos}")

        if possui_else:
            self.codigo.append(f"Else{self.contador_rotulos}: NADA")
            for cmd in no.bloco_false:
                self.visita(cmd)

        self.codigo.append(f"FimCond{self.contador_rotulos}: NADA")
        self.contador_rotulos += 1
    
    def visita_CmdRepeticao(self, no: CmdRepeticao):
        self.visita(no.expr)

        self.codigo.append(f"InicioLaco{self.contador_rotulos}: NADA")
        self.codigo.append(f"DSVF FimLaco{self.contador_rotulos}")

        for cmd in no.bloco:
            self.visita(cmd)

        self.codigo.append(f"DSVS InicioLaco{self.contador_rotulos}")
        self.codigo.append(f"FimLaco{self.contador_rotulos}: NADA")
        self.contador_rotulos += 1
        
        