from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import (
    atualizar_com_operacao,
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
        },
        {
            "nome": "data",
            "tipo": "DATA"
        }
    ]
)

inserir_em(
    banco,
    "produto",
    [
        Token("Notebook", True),
        Token(10, False),
        Token(3000.0, False),
        Token("28/02/2028", True)
    ]
)
print("\n=== REGISTRO ORIGINAL ===")
mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 1 - SOMAR INTEIRO ===")
quantidade = atualizar_com_operacao(
    banco,
    "produto",
    "estoque",
    "+",
    Token(5, False),
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 2 - SUBTRAIR DECIMAL ===")
quantidade = atualizar_com_operacao(
    banco,
    "produto",
    "preco",
    "-",
    Token(500.0, False),
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 3 - CONCATENAR TEXTO ===")
quantidade = atualizar_com_operacao(
    banco,
    "produto",
    "nome",
    "+",
    Token(" Pro", True),
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 4 - SOMAR DIAS EM DATA ===")
quantidade = atualizar_com_operacao(
    banco,
    "produto",
    "data",
    "+",
    Token(1, False),
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "produto"
)

print("\n=== TESTE 5 - OPERACAO COM TIPOS DIFERENTES ===")
try:
    atualizar_com_operacao(
        banco,
        "produto",
        "estoque",
        "+",
        Token(2.5, False),
        "id",
        "==",
        Token(1, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 6 - DIVISAO POR ZERO ===")
try:
    atualizar_com_operacao(
        banco,
        "produto",
        "preco",
        "/",
        Token(0.0, False),
        "id",
        "==",
        Token(1, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== REGISTRO FINAL ===")
mostrar_dados(
    banco,
    "produto"
)
print("\n=== TESTES DE ATUALIZACAO COM OPERACOES FINALIZADOS ===")