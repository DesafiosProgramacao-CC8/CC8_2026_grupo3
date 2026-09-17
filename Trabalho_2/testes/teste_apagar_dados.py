from banco import BancoDados
from operacoes import criar_tabela, inserir_em
from token import Token
from erros import ErroIFFARQL

from consultas import apagar_dados, mostrar_dados

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

print("\n=== REGISTROS ANTES DA REMOCAO ===")
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 1 - APAGAR COM ONDE ===")
quantidade = apagar_dados(
    banco,
    "pessoa",
    "idade",
    "<",
    Token(18, False)
)
print("Quantidade removida:", quantidade)

print("\n=== REGISTROS DEPOIS DA REMOCAO ===")
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTE 2 - VERIFICAR PROXIMO ID ===")
tabela = banco.buscar_tabela("pessoa")
print("Proximo id antes da nova insercao:", tabela.proximo_id)
novo_registro = inserir_em(
    banco,
    "pessoa",
    [
        Token("Carlos", True),
        Token(40, False)
    ]
)
print("Novo registro:", novo_registro.valores)
print("Proximo id depois da insercao:", tabela.proximo_id)

print("\n=== TESTE 3 - CONDICAO SEM RESULTADOS ===")
quantidade = apagar_dados(
    banco,
    "pessoa",
    "idade",
    ">",
    Token(100, False)
)
print("Quantidade removida:", quantidade)

print("\n=== TESTE 4 - COLUNA INEXISTENTE ===")
try:
    apagar_dados(
        banco,
        "pessoa",
        "salario",
        ">",
        Token(1000, False)
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 5 - TABELA INEXISTENTE ===")
try:
    apagar_dados(
        banco,
        "produto"
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 6 - APAGAR TODOS OS REGISTROS ===")
quantidade = apagar_dados(
    banco,
    "pessoa"
)
print("Quantidade removida:", quantidade)

print("\n=== REGISTROS APOS APAGAR TODOS ===")
mostrar_dados(
    banco,
    "pessoa"
)

print("\n=== TESTES DE APAGADADOSDE FINALIZADOS ===")