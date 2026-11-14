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

        if no.decFuncoes:        
            self.codigo.append("DSVS FimDecFuncProgram")
            self.codigo.append("DecFuncProgram: NADA")
            for decFun in no.decFuncoes:
                self.visita(decFun)
            self.codigo.append("FimDecFuncProgram: NADA")
        
        for cmd in no.comandos:
            self.visita(cmd)

        self.codigo.append(f"DMEM {len(no.decVariaveis)}")
        self.codigo.append("PARA")
        self.codigo.append("FIM")
    
    def visita_DeclaraFuncao(self, no: DeclaraFuncao):
        self.codigo.append(f"Func{self.contador_rotulos}: NADA")
        no.simbolo.rotulo = f"Func{self.contador_rotulos}"
        self.codigo.append(f"ENPR {no.nivel_lexico}")
        for decVar in no.decVariaveis:
            self.visita(decVar)
        
        if no.decFuncoes:
            self.codigo.append(f"DSCS FimDecFunc{self.contador_rotulos}")
            self.codigo.append(f"DecFunc{self.contador_rotulos}: NADA")
            for decFun in no.decFuncoes:
                self.visita(decFun)
            self.codigo.append(f"FimDecFunc{self.contador_rotulos}: NADA")
        
        for cmd in no.comandos:
            self.visita(cmd)
            
        self.contador_rotulos += 1

        tamanho_memoria_alocada = len(no.decVariaveis)
        self.codigo.append(f"DMEM {tamanho_memoria_alocada}")

    def visita_DeclaraVariavel(self, no: DeclaraVariavel):
        # mudar para alocar várias de uma vez
        self.codigo.append("AMEM 1")
        if no.expr is not None:
            self.visita(no.expr)
            s : SimboloVariavel = no.simbolo
            self.codigo.append(f"ARMZ {s.nivel_lexico},{s.endereco}")

    def visita_CmdAtribuicao(self, no: CmdAtribuicao):
        s : SimboloVariavel = no.simbolo_id
        self.visita(no.expr)
        self.codigo.append(f"ARMZ {s.nivel_lexico},{s.endereco}")

    def visita_CmdChamada(self, no: CmdChamada):
        self.visita(no.chamada)
        if no.chamada.tipo != VOID:
            self.codigo.append("DMEM 1")

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

    def visita_CmdRetorno(self, no: CmdRetorno):
        if no.expr is not None:
            self.visita(no.expr)
            self.codigo.append(f"ARMZ {no.nivel_lexico},-{5+no.numero_variaveis}")

        self.codigo.append(f"RTPR {no.numero_variaveis}")

    def visita_CmdLeitura(self, no: CmdLeitura):
        for s in no.simbolos_params.values():
            self.codigo.append("LEIT")
            self.codigo.append(f"ARMZ {s.nivel_lexico},{s.endereco}")

    def visita_CmdEscrita(self, no: CmdEscrita):
        for expr in no.exprs:
            self.visita(expr)
            self.codigo.append("IMPR")

    def visita_OpAritmetica(self, no: OpAritmetica):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)

        op = {'+': 'SOMA', '-': 'SUBT', '*': 'MULT', '/':'DIVI'}
        self.codigo.append(op[no.op])

    def visita_OpRelacional(self, no: OpRelacional):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        op = {'<':'CMME', '>': 'CMMA', '<=':'CMEG', '>=':'CMAG'}
        self.codigo.append(op[no.op])

    def visita_OpIgualdade(self, no: OpIgualdade):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        self.codigo.append({'==':'CMIG', '!=':'CMDG'}[no.op])

    def visita_OpLogica(self, no: OpLogica):
        self.visita(no.ladoEsq)
        self.visita(no.ladoDir)
        self.codigo.append({'&&':'CONJ', '||':'DISJ'}[no.op])

    def visita_OpUn(self, no: OpUn):
        self.visita(no.expr)
        self.codigo.append({'-': 'INVR', '!':'NEGA'}[no.op])

    def visita_Numero(self, no: Numero):
        self.codigo.append(f"CRCT {no.valor}")

    def visita_Booleano(self, no: Booleano):
        self.codigo.append(f"CRCT {"1" if no.valor else "0"}")

    def visita_Chamada(self, no: Chamada):
        if no.tipo != VOID:
            self.codigo.append("AMEM 1")
        
        for param in no.params:
            self.visita(param)

        s : SimboloFuncao = no.simbolo
        self.codigo.append(f"CHPR {s.rotulo},{s.nivel_lexico}")

    def visita_Id(self, no: Id):
        s : Simbolo = no.simbolo
        self.codigo.append(f"CRVL {s.nivel_lexico},{s.endereco}")
