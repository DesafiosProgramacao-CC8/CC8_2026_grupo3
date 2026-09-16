from tabela import Tabela
from coluna import Coluna
from registro import Registro
from erros import ErroIFFARQL

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
        raise ErroIFFARQL("Tipo de dado inválido")


def criar_tabela(banco, nome_tabela, definicoes):

    if banco.existe_tabela(nome_tabela):
        raise ErroIFFARQL("Tabela já existe")

    tabela = Tabela(nome_tabela)

    for definicao in definicoes:

        nome_coluna = definicao["nome"]
        tipo_coluna = definicao["tipo"]

        tipo = criar_tipo(tipo_coluna)

        chave_estrangeira = definicao.get("chave_estrangeira")

        if chave_estrangeira is not None:

            if tipo_coluna != "INTEIRO":
                raise ErroIFFARQL(
                    "Chave estrangeira só pode ser do tipo INTEIRO"
                )

            if not banco.existe_tabela(chave_estrangeira):
                raise ErroIFFARQL(
                    "Tabela de referência não encontrada"
                )

        coluna = Coluna(
            nome_coluna,
            tipo,
            chave_estrangeira
        )

        tabela.adicionar_coluna(coluna)

    banco.adicionar_tabela(tabela)

    return tabela


def apagar_tabela(banco, nome_tabela):

    if not banco.existe_tabela(nome_tabela):
        raise ErroIFFARQL("Tabela não encontrada")

    tabela = banco.buscar_tabela(nome_tabela)

    if not tabela.arvore.esta_vazia():
        raise ErroIFFARQL(
            "Não é possível apagar uma tabela com registros"
        )

    for outra_tabela in banco.tabelas.values():

        if outra_tabela.nome == nome_tabela:
            continue

        for coluna in outra_tabela.colunas:

            if coluna.chave_estrangeira == nome_tabela:
                raise ErroIFFARQL(
                    "Não é possível apagar uma tabela referenciada por chave estrangeira"
                )

    del banco.tabelas[nome_tabela]


def inserir_em(banco, nome_tabela, valores):

    if not banco.existe_tabela(nome_tabela):
        raise ErroIFFARQL("Tabela não encontrada")

    tabela = banco.buscar_tabela(nome_tabela)

    # Ignora a coluna id, pois ela é automática
    colunas = tabela.colunas[1:]

    if len(valores) != len(colunas):
        raise ErroIFFARQL(
            "Quantidade de valores inválida"
        )

    dados = {}

    for coluna, valor in zip(colunas, valores):

        if valor is None:
            raise ErroIFFARQL(
                "Valores nulos não são permitidos"
            )

        if not coluna.validar_valor(valor):
            raise ErroIFFARQL(
                f"Valor inválido para a coluna {coluna.nome}"
            )

        # Verifica chave estrangeira
        if coluna.chave_estrangeira is not None:

            tabela_referenciada = banco.buscar_tabela(
                coluna.chave_estrangeira
            )

            registro_referenciado = (
                tabela_referenciada.arvore.buscar(valor)
            )

            if registro_referenciado is None:
                raise ErroIFFARQL(
                    "Chave estrangeira inexistente"
                )

        dados[coluna.nome] = valor

    novo_id = tabela.gerar_id()

    registro = Registro(
        novo_id,
        dados
    )

    tabela.arvore.inserir(
        novo_id,
        registro
    )

    return registro