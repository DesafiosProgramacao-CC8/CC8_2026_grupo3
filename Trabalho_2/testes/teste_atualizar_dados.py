from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import atualizar_dados, mostrar_dados

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

print("\n=== REGISTROS ANTES DAS ATUALIZACOES ===")
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 1 - ATUALIZAR UM REGISTRO COM ONDE ===")
quantidade = atualizar_dados(
    banco,
    "pessoa",
    "idade",
    Token(18, False),
    "id",
    "==",
    Token(2, False)
)

print("Quantidade atualizada:", quantidade)
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 2 - ATUALIZAR TEXTO ===")
quantidade = atualizar_dados(
    banco,
    "pessoa",
    "nome",
    Token("Maria Silva", True),
    "id",
    "==",
    Token(1, False)
)

print("Quantidade atualizada:", quantidade)
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 3 - ATUALIZAR TODOS SEM ONDE ===")
quantidade = atualizar_dados(
    banco,
    "pessoa",
    "idade",
    Token(40, False)
)

print("Quantidade atualizada:", quantidade)
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 4 - TENTAR ALTERAR ID ===")
try:
    atualizar_dados(
        banco,
        "pessoa",
        "id",
        Token(50, False),
        "id",
        "==",
        Token(1, False)
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 5 - COLUNA INEXISTENTE ===")
try:
    atualizar_dados(
        banco,
        "pessoa",
        "salario",
        Token(5000, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTE 6 - TIPO INVALIDO ===")
try:
    atualizar_dados(
        banco,
        "pessoa",
        "idade",
        Token("quarenta", True)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 7 - VALOR NULO ===")
try:
    atualizar_dados(
        banco,
        "pessoa",
        "idade",
        Token(None, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 8 - ONDE SEM RESULTADOS ===")
quantidade = atualizar_dados(
    banco,
    "pessoa",
    "idade",
    Token(50, False),
    "id",
    "==",
    Token(999, False)
)
print("Quantidade atualizada:", quantidade)

print("\n=== PREPARANDO TESTES DE CHAVE ESTRANGEIRA ===")
criar_tabela(
    banco,
    "pedido",
    [
        {
            "nome": "descricao",
            "tipo": "TEXTO"
        },
        {
            "nome": "idCliente",
            "tipo": "INTEIRO",
            "chave_estrangeira": "pessoa"
        }
    ]
)

pedido = inserir_em(
    banco,
    "pedido",
    [
        Token("Notebook", True),
        Token(1, False)
    ]
)
print("Pedido antes da atualização:")
print(pedido.valores)


print("\n=== TESTE 9 - ATUALIZAR CHAVE ESTRANGEIRA VALIDA ===")
quantidade = atualizar_dados(
    banco,
    "pedido",
    "idCliente",
    Token(2, False),
    "id",
    "==",
    Token(1, False)
)
print("Quantidade atualizada:", quantidade)

mostrar_dados(
    banco,
    "pedido"
)

print("\n=== TESTE 10 - ATUALIZAR CHAVE ESTRANGEIRA INVALIDA ===")
try:
    atualizar_dados(
        banco,
        "pedido",
        "idCliente",
        Token(999, False),
        "id",
        "==",
        Token(1, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("Pedido após tentativa inválida:")

mostrar_dados(
    banco,
    "pedido"
)

print("\n=== TESTES DE ATUALIZATABELA FINALIZADOS ===")