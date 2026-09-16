from coluna import Coluna
from tipos.inteiro import Inteiro

class Tabela:
    def __init__(self, nome):
        self.nome = nome
        self.colunas = [
            Coluna("id", Inteiro())
        ]
        self.proximo_id = 1

    def adicionar_coluna(self, coluna):
        if coluna.nome=="id":
            raise Exception("Não é permitido criar uma coluna chamada id'.")

        for coluna_existete in self.colunas:
            if coluna_existete.nome == coluna.nome:
                raise Exception(f"Já existe uma coluna com o nome '{coluna.nome}'.")
            
        self.colunas.append(coluna)

    def gerar_id(self):
        id_atual = self.proximo_id
        self.proximo_id += 1
        return id_atual