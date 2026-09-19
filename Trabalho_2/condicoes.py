from erros import ErroIFFARQL
from tipos.booleano import Booleano
from tipos.data import Data
from tipos.texto import Texto


OPERADORES_VALIDOS = ["<", "<=", ">", ">=", "==", "<>"]


# Busca uma coluna pelo nome dentro da tabela.
def buscar_coluna(tabela, nome_coluna):
    for coluna in tabela.colunas:
        if coluna.nome == nome_coluna:
            return coluna

    raise ErroIFFARQL(
        f"Coluna '{nome_coluna}' não encontrada."
    )


# Verifica se o operador existe e se pode ser utilizado com o tipo da coluna.
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


# Verifica se o valor e o uso de aspas são compatíveis com o tipo da coluna.
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


# Converte uma DATA para ano, mês e dia, permitindo a comparação cronológica.
def converter_data(valor):
    dia, mes, ano = valor.split("/")

    return (
        int(ano),
        int(mes),
        int(dia)
    )


# Executa a comparação entre dois valores usando o operador informado.
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


# Avalia se um registro atende à condição informada após a palavra ONDE.
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