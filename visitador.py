class Visitador:
    def visita(self, no):
        if no is None:
            return
        nome_metodo = f'visita_{type(no).__name__}'
        visitor = getattr(self, nome_metodo, self.visita_padrao)
        return visitor(no)

    def visita_padrao(self, no):
        raise NotImplementedError(f"Visita não implementada: {type(no).__name__}")