from coluna import Coluna
from tipos.inteiro import Inteiro
from arvore import ArvoreRegistros
from erros import ErroIFFARQL


class Tabela:
    def __init__(self, nome):
        self.nome = nome
        self.colunas = [
            Coluna("id", Inteiro())
        ]
        self.proximo_id = 1
        self.arvore = ArvoreRegistros()

    def adicionar_coluna(self, coluna):
        if coluna.nome == "id":
            raise ErroIFFARQL("Não é permitido criar uma coluna chamada id.")

        for coluna_existente in self.colunas:
            if coluna_existente.nome == coluna.nome:
                raise ErroIFFARQL(
                    f"Já existe uma coluna com o nome '{coluna.nome}'."
                )

        self.colunas.append(coluna)

    def gerar_id(self):
        id_atual = self.proximo_id
        self.proximo_id += 1
        return id_atual

    def obter_proximo_id(self):
        return self.proximo_id

    def definir_proximo_id(self, valor):
        self.proximo_id = valor