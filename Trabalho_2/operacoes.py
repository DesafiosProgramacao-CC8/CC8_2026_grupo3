from tabela import Tabela
from coluna import Coluna

from tipos.inteiro import Inteiro
from tipos.decimal import Decimal
from tipos.texto import Texto
from tipos.data import Data
from tipos.booleano import Booleano


def criar_tipo(nome_tipo):
    if nome_tipo == "INTEIRO":
        return Inteiro()

    elif nome_tipo == "DECIMAL":
        return Decimal()

    elif nome_tipo == "TEXTO":
        return Texto()

    elif nome_tipo == "DATA":
        return Data()

    elif nome_tipo == "BOOLEANO":
        return Booleano()

    else:
        raise Exception("Tipo de dado inválido")


def criar_tabela(banco, nome_tabela, definicoes):

    if banco.existe_tabela(nome_tabela):
        raise Exception("Tabela já existe")

    tabela = Tabela(nome_tabela)

    for definicao in definicoes:
        nome_coluna = definicao["nome"]
        tipo_coluna = definicao["tipo"]

        tipo = criar_tipo(tipo_coluna)

        chave_estrangeira = definicao.get("chave_estrangeira")

        if chave_estrangeira is not None:
            
            if tipo_coluna != "INTEIRO":
                raise Exception("Chave estrangeira só pode ser do tipo INTEIRO")

            if not banco.existe_tabela(chave_estrangeira):
                raise Exception("Tabela de referência não encontrada")
        coluna = Coluna(
            nome_coluna,
            tipo,
            chave_estrangeira
        )

        tabela.adicionar_coluna(coluna)

    banco.adicionar_tabela(tabela)

    return tabela