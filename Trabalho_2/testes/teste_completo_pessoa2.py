#Plano de teste completo com a utilização de asserts para verificar se os resultados estão corretos, gerado com auxilio de IA.

from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL
from consultas import (mostrar_dados, apagar_dados, atualizar_dados, atualizar_com_operacao, atualizar_multiplos)
from condicoes import avaliar_condicao

banco = BancoDados()

print("========================================")
print(" TESTE COMPLETO - FUNCIONALIDADES PESSOA 2")
print("========================================")

# PREPARAÇÃO DO BANCO
print("\n=== 1. PREPARANDO O BANCO ===")
criar_tabela(
    banco,
    "cliente",
    [
        {
            "nome": "nome",
            "tipo": "TEXTO"
        },
        {
            "nome": "idade",
            "tipo": "INTEIRO"
        },
        {
            "nome": "saldo",
            "tipo": "DECIMAL"
        },
        {
            "nome": "ativo",
            "tipo": "BOOLEANO"
        },
        {
            "nome": "cadastro",
            "tipo": "DATA"
        }
    ]
)

cliente1 = inserir_em(
    banco,
    "cliente",
    [
        Token("Maria", True),
        Token(25, False),
        Token(1000.0, False),
        Token(True, False),
        Token("28/02/2028", True)
    ]
)

cliente2 = inserir_em(
    banco,
    "cliente",
    [
        Token("Joao", True),
        Token(17, False),
        Token(500.0, False),
        Token(False, False),
        Token("10/01/2026", True)
    ]
)

cliente3 = inserir_em(
    banco,
    "cliente",
    [
        Token("Ana", True),
        Token(30, False),
        Token(2000.0, False),
        Token(True, False),
        Token("01/01/2025", True)
    ]
)

assert cliente1.id == 1
assert cliente2.id == 2
assert cliente3.id == 3

print("OK - banco preparado")

# ONDE E COMPARADORES
print("\n=== 2. TESTANDO ONDE E COMPARADORES ===")
tabela_cliente = banco.buscar_tabela("cliente")

assert avaliar_condicao(
    tabela_cliente,
    cliente1,
    "idade",
    ">=",
    Token(18, False)
) is True

assert avaliar_condicao(
    tabela_cliente,
    cliente2,
    "idade",
    ">=",
    Token(18, False)
) is False

assert avaliar_condicao(
    tabela_cliente,
    cliente1,
    "nome",
    "==",
    Token("Maria", True)
) is True

assert avaliar_condicao(
    tabela_cliente,
    cliente1,
    "ativo",
    "==",
    Token(True, False)
) is True

assert avaliar_condicao(
    tabela_cliente,
    cliente1,
    "cadastro",
    ">",
    Token("01/01/2028", True)
) is True

print("OK - ONDE e comparadores")

# MOSTRADADOSDE
print("\n=== 3. TESTANDO MOSTRADADOSDE ===")
print("Todos os clientes:")
mostrar_dados(
    banco,
    "cliente"
)

print("\nClientes maiores de idade:")
mostrar_dados(
    banco,
    "cliente",
    "idade",
    ">=",
    Token(18, False)
)

print("OK - MOSTRADADOSDE")

# APAGADADOSDE
print("\n=== 4. TESTANDO APAGADADOSDE ===")
quantidade = apagar_dados(
    banco,
    "cliente",
    "id",
    "==",
    Token(2, False)
)

assert quantidade == 1
assert tabela_cliente.arvore.buscar(2) is None
print("OK - APAGADADOSDE com ONDE")

# Verifica se o ID apagado não será reutilizado.
novo_cliente = inserir_em(
    banco,
    "cliente",
    [
        Token("Carlos", True),
        Token(40, False),
        Token(3000.0, False),
        Token(True, False),
        Token("01/01/2026", True)
    ]
)

assert novo_cliente.id == 4
print("OK - id removido não foi reutilizado")

# INTEGRIDADE REFERENCIAL
print("\n=== 5. TESTANDO INTEGRIDADE REFERENCIAL ===")
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

pedido = inserir_em(
    banco,
    "pedido",
    [
        Token("Notebook", True),
        Token(1, False)
    ]
)

try:
    apagar_dados(
        banco,
        "cliente",
        "id",
        "==",
        Token(1, False)
    )

    assert False, "Era esperado erro de integridade referencial."
except ErroIFFARQL:
    pass

assert tabela_cliente.arvore.buscar(1) is not None
print("OK - registro referenciado não foi removido")

# ATUALIZAÇÃO SIMPLES
print("\n=== 6. TESTANDO ATUALIZACAO SIMPLES ===")
quantidade = atualizar_dados(
    banco,
    "cliente",
    "idade",
    Token(26, False),
    "id",
    "==",
    Token(1, False)
)

assert quantidade == 1
assert cliente1.valores["idade"] == 26

print("OK - atualização simples")

# PROIBIÇÃO DE ALTERAR ID
print("\n=== 7. TESTANDO PROIBICAO DE ALTERAR ID ===")
try:
    atualizar_dados(
        banco,
        "cliente",
        "id",
        Token(100, False),
        "id",
        "==",
        Token(1, False)
    )

    assert False, "Era esperado erro ao tentar alterar id."
except ErroIFFARQL:
    pass

assert cliente1.id == 1
print("OK - id protegido")

# OPERAÇÕES POLIMÓRFICAS
print("\n=== 8. TESTANDO OPERACOES ===")
# INTEIRO
atualizar_com_operacao(
    banco,
    "cliente",
    "idade",
    "+",
    Token(4, False),
    "id",
    "==",
    Token(1, False)
)

assert cliente1.valores["idade"] == 30

# DECIMAL
atualizar_com_operacao(
    banco,
    "cliente",
    "saldo",
    "+",
    Token(500.0, False),
    "id",
    "==",
    Token(1, False)
)
assert cliente1.valores["saldo"] == 1500.0

# TEXTO
atualizar_com_operacao(
    banco,
    "cliente",
    "nome",
    "+",
    Token(" Silva", True),
    "id",
    "==",
    Token(1, False)
)

assert cliente1.valores["nome"] == "Maria Silva"

# DATA + INTEIRO
atualizar_com_operacao(
    banco,
    "cliente",
    "cadastro",
    "+",
    Token(1, False),
    "id",
    "==",
    Token(1, False)
)

assert cliente1.valores["cadastro"] == "29/02/2028"

print("OK - operações polimórficas")

# DIVISÃO POR ZERO
print("\n=== 9. TESTANDO DIVISAO POR ZERO ===")
saldo_antes = cliente1.valores["saldo"]

try:
    atualizar_com_operacao(
        banco,
        "cliente",
        "saldo",
        "/",
        Token(0.0, False),
        "id",
        "==",
        Token(1, False)
    )

    assert False, "Era esperado erro de divisão por zero."
except ErroIFFARQL:
    pass

assert cliente1.valores["saldo"] == saldo_antes

print("OK - divisão por zero bloqueada")

# MÚLTIPLOS COM
print("\n=== 10. TESTANDO MULTIPLAS ATUALIZACOES ===")

atualizacoes = [
    {
        "coluna": "idade",
        "operador": "+",
        "token": Token(5, False)
    },
    {
        "coluna": "saldo",
        "operador": "+",
        "token": Token(500.0, False)
    }
]

quantidade = atualizar_multiplos(
    banco,
    "cliente",
    atualizacoes,
    "id",
    "==",
    Token(1, False)
)

assert quantidade == 1
assert cliente1.valores["idade"] == 35
assert cliente1.valores["saldo"] == 2000.0

print("OK - múltiplos COM")

# ATOMICIDADE
print("\n=== 11. TESTANDO ATOMICIDADE ===")

idade_antes = cliente1.valores["idade"]
saldo_antes = cliente1.valores["saldo"]

atualizacoes_invalidas = [
    {
        "coluna": "idade",
        "operador": "+",
        "token": Token(10, False)
    },
    {
        "coluna": "saldo",
        "operador": "/",
        "token": Token(0.0, False)
    }
]

try:
    atualizar_multiplos(
        banco,
        "cliente",
        atualizacoes_invalidas,
        "id",
        "==",
        Token(1, False)
    )

    assert False, "Era esperado erro durante atualização múltipla."
except ErroIFFARQL:
    pass

assert cliente1.valores["idade"] == idade_antes
assert cliente1.valores["saldo"] == saldo_antes

print("OK - atomicidade preservada")

# CHAVE ESTRANGEIRA NA ATUALIZAÇÃO
print("\n=== 12. TESTANDO FK NA ATUALIZACAO ===")
quantidade = atualizar_dados(
    banco,
    "pedido",
    "idCliente",
    Token(3, False),
    "id",
    "==",
    Token(1, False)
)

assert quantidade == 1
assert pedido.valores["idCliente"] == 3

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

    assert False, "Era esperado erro de chave estrangeira."
except ErroIFFARQL:
    pass

assert pedido.valores["idCliente"] == 3
print("OK - chave estrangeira validada")

# ERROS DE TIPO E COLUNA
print("\n=== 13. TESTANDO ERROS ===")
try:
    atualizar_dados(
        banco,
        "cliente",
        "coluna_inexistente",
        Token(10, False)
    )

    assert False, "Era esperado erro de coluna inexistente."
except ErroIFFARQL:
    pass

try:
    atualizar_dados(
        banco,
        "cliente",
        "idade",
        Token("trinta", True)
    )

    assert False, "Era esperado erro de tipo incompatível."
except ErroIFFARQL:
    pass
print("OK - erros tratados")

# RESULTADO FINAL
print("\n=== ESTADO FINAL DO BANCO ===")
print("\nClientes:")
mostrar_dados(
    banco,
    "cliente"
)

print("\nPedidos:")
mostrar_dados(
    banco,
    "pedido"
)

print("\n========================================")
print(" TODOS OS TESTES DA PESSOA 2 PASSARAM")
print("========================================")