from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import apagar_dados, mostrar_dados

banco = BancoDados()

print("=== PREPARANDO TABELAS PARA OS TESTES ===")
criar_tabela(
    banco,
    "cliente",
    [
        {
            "nome": "nome",
            "tipo": "TEXTO"
        }
    ]
)

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
            "chave_estrangeira": "cliente"
        }
    ]
)

cliente1 = inserir_em(
    banco,
    "cliente",
    [
        Token("Maria", True)
    ]
)

cliente2 = inserir_em(
    banco,
    "cliente",
    [
        Token("Joao", True)
    ]
)

inserir_em(
    banco,
    "pedido",
    [
        Token("Notebook", True),
        Token(1, False)
    ]
)

print("\n=== CLIENTES ANTES DOS TESTES ===")
mostrar_dados(
    banco,
    "cliente"
)

print("\n=== PEDIDOS ANTES DOS TESTES ===")
mostrar_dados(
    banco,
    "pedido"
)

print("\n=== TESTE 1 - APAGAR REGISTRO REFERENCIADO ===")
try:
    apagar_dados(
        banco,
        "cliente",
        "id",
        "==",
        Token(1, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== CLIENTES APOS TENTATIVA INVALIDA ===")
mostrar_dados(
    banco,
    "cliente"
)

print("\n=== TESTE 2 - APAGAR REGISTRO NAO REFERENCIADO ===")
quantidade = apagar_dados(
    banco,
    "cliente",
    "id",
    "==",
    Token(2, False)
)
print("Quantidade removida:", quantidade)

print("\n=== CLIENTES APOS REMOCAO VALIDA ===")
mostrar_dados(
    banco,
    "cliente"
)

print("\n=== TESTE 3 - VERIFICAR ATOMICIDADE DA REMOCAO ===")
cliente3 = inserir_em(
    banco,
    "cliente",
    [
        Token("Ana", True)
    ]
)

cliente4 = inserir_em(
    banco,
    "cliente",
    [
        Token("Carlos", True)
    ]
)

print("Clientes antes da tentativa de apagar todos:")
mostrar_dados(
    banco,
    "cliente"
)
try:
    apagar_dados(
        banco,
        "cliente"
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\nClientes depois da tentativa de apagar todos:")
mostrar_dados(
    banco,
    "cliente"
)

print("\n=== TESTES DE INTEGRIDADE FINALIZADOS ===")