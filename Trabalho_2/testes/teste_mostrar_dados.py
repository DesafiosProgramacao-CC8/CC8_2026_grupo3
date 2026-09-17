from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import mostrar_dados

banco = BancoDados()

print("=== PREPARANDO TABELA PARA OS TESTES ===")
criar_tabela(
    banco,
    "pessoa",
    [
        {
            "nome": "nome",
            "tipo": "TEXTO"
        },
        {
            "nome": "idade",
            "tipo": "INTEIRO"
        }
    ]
)

inserir_em(
    banco,
    "pessoa",
    [
        Token("Maria", True),
        Token(25, False)
    ]
)

inserir_em(
    banco,
    "pessoa",
    [
        Token("Joao", True),
        Token(17, False)
    ]
)

inserir_em(
    banco,
    "pessoa",
    [
        Token("Ana", True),
        Token(30, False)
    ]
)


print("\n=== TESTE 1 - MOSTRAR TODOS OS REGISTROS ===")
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 2 - MOSTRAR COM ONDE ===")
mostrar_dados(
    banco,
    "pessoa",
    "idade",
    ">=",
    Token(18, False)
)

print("\n=== TESTE 3 - CONSULTA SEM RESULTADOS ===")
mostrar_dados(
    banco,
    "pessoa",
    "idade",
    ">",
    Token(100, False)
)

print("\n=== TESTE 4 - CONSULTA PELO ID ===")
mostrar_dados(
    banco,
    "pessoa",
    "id",
    "==",
    Token(2, False)
)

print("\n=== TESTE 5 - TABELA INEXISTENTE ===")
try:
    mostrar_dados(
        banco,
        "produto"
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTE 6 - COLUNA INEXISTENTE NO ONDE ===")
try:
    mostrar_dados(
        banco,
        "pessoa",
        "salario",
        ">",
        Token(1000, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTES DE MOSTRADADOSDE FINALIZADOS ===")