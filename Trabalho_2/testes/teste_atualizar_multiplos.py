from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import (
    atualizar_multiplos,
    mostrar_dados
)

banco = BancoDados()

print("=== PREPARANDO TABELA PARA OS TESTES ===")
criar_tabela(
    banco,
    "produto",
    [
        {
            "nome": "nome",
            "tipo": "TEXTO"
        },
        {
            "nome": "estoque",
            "tipo": "INTEIRO"
        },
        {
            "nome": "preco",
            "tipo": "DECIMAL"
        }
    ]
)

inserir_em(
    banco,
    "produto",
    [
        Token("Notebook", True),
        Token(10, False),
        Token(3000.0, False)
    ]
)

inserir_em(
    banco,
    "produto",
    [
        Token("Mouse", True),
        Token(20, False),
        Token(100.0, False)
    ]
)

print("\n=== REGISTROS ORIGINAIS ===")
mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 1 - MULTIPLAS ATUALIZACOES COM ONDE ===")
atualizacoes = [
    {
        "coluna": "estoque",
        "operador": "+",
        "token": Token(5, False)
    },
    {
        "coluna": "preco",
        "operador": "-",
        "token": Token(500.0, False)
    },
    {
        "coluna": "nome",
        "operador": "+",
        "token": Token(" Pro", True)
    }
]

quantidade = atualizar_multiplos(
    banco,
    "produto",
    atualizacoes,
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 2 - MULTIPLAS ATUALIZACOES SEM ONDE ===")
atualizacoes = [
    {
        "coluna": "estoque",
        "operador": "+",
        "token": Token(1, False)
    }
]

quantidade = atualizar_multiplos(
    banco,
    "produto",
    atualizacoes
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 3 - ATRIBUICAO SIMPLES EM MULTIPLOS COM ===")
atualizacoes = [
    {
        "coluna": "nome",
        "operador": None,
        "token": Token("Produto atualizado", True)
    },
    {
        "coluna": "estoque",
        "operador": None,
        "token": Token(50, False)
    }
]

quantidade = atualizar_multiplos(
    banco,
    "produto",
    atualizacoes,
    "id",
    "==",
    Token(2, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 4 - ATOMICIDADE COM OPERACAO INVALIDA ===")
print("Registro antes da tentativa inválida:")
mostrar_dados(
    banco,
    "produto",
    "id",
    "==",
    Token(1, False)
)

atualizacoes = [
    {
        "coluna": "estoque",
        "operador": "+",
        "token": Token(10, False)
    },
    {
        "coluna": "preco",
        "operador": "/",
        "token": Token(0.0, False)
    }
]

try:
    atualizar_multiplos(
        banco,
        "produto",
        atualizacoes,
        "id",
        "==",
        Token(1, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("Registro depois da tentativa inválida:")
mostrar_dados(
    banco,
    "produto",
    "id",
    "==",
    Token(1, False)
)

print("\n=== TESTE 5 - TENTAR ALTERAR ID ===")
atualizacoes = [
    {
        "coluna": "id",
        "operador": None,
        "token": Token(100, False)
    }
]

try:
    atualizar_multiplos(
        banco,
        "produto",
        atualizacoes
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTE 6 - COLUNA INEXISTENTE ===")
atualizacoes = [
    {
        "coluna": "peso",
        "operador": None,
        "token": Token(10, False)
    }
]

try:
    atualizar_multiplos(
        banco,
        "produto",
        atualizacoes
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTES DE MULTIPLAS ATUALIZACOES FINALIZADOS ===")