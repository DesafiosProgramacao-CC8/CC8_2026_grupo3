from erros import ErroIFFARQL
from tipos.booleano import Booleano
from tipos.data import Data
from tipos.texto import Texto


OPERADORES_VALIDOS = ["<", "<=", ">", ">=", "==", "<>"]


def buscar_coluna(tabela, nome_coluna):
    for coluna in tabela.colunas:
        if coluna.nome == nome_coluna:
            return coluna

    raise ErroIFFARQL(
        f"Coluna '{nome_coluna}' não encontrada."
    )


def validar_operador(coluna, operador):
    if operador not in OPERADORES_VALIDOS:
        raise ErroIFFARQL(
            f"Operador '{operador}' inválido."
        )

    if isinstance(coluna.tipo, Booleano):
        if operador not in ["==", "<>"]:
            raise ErroIFFARQL(
                f"Operador '{operador}' não permitido para BOOLEANO."
            )


def validar_token(coluna, token):
    valor = token.obter_valor()

    if isinstance(coluna.tipo, (Texto, Data)):
        if not token.possui_aspas():
            raise ErroIFFARQL(
                f"Valor da coluna '{coluna.nome}' deve estar entre aspas."
            )
    else:
        if token.possui_aspas():
            raise ErroIFFARQL(
                f"Valor da coluna '{coluna.nome}' não deve estar entre aspas."
            )

    if not coluna.validar_valor(valor):
        raise ErroIFFARQL(
            f"Valor incompatível com o tipo da coluna '{coluna.nome}'."
        )


def converter_data(valor):
    dia, mes, ano = valor.split("/")

    return (
        int(ano),
        int(mes),
        int(dia)
    )


def comparar(valor_registro, operador, valor_condicao):
    if operador == "==":
        return valor_registro == valor_condicao

    if operador == "<>":
        return valor_registro != valor_condicao

    if operador == "<":
        return valor_registro < valor_condicao

    if operador == "<=":
        return valor_registro <= valor_condicao

    if operador == ">":
        return valor_registro > valor_condicao

    if operador == ">=":
        return valor_registro >= valor_condicao


def avaliar_condicao(tabela, registro, nome_coluna, operador, token):
    coluna = buscar_coluna(tabela, nome_coluna)

    validar_operador(coluna, operador)
    validar_token(coluna, token)

    valor_registro = registro.obter_valores(nome_coluna)
    valor_condicao = token.obter_valor()

    if isinstance(coluna.tipo, Data):
        valor_registro = converter_data(valor_registro)
        valor_condicao = converter_data(valor_condicao)

    return comparar(
        valor_registro,
        operador,
        valor_condicao
    )