from banco import BancoDados
from operacoes import criar_tabela, inserir_em, apagar_tabela
from erros import ErroIFFARQL


banco = BancoDados()


print("=== CRIANDO TABELA CLIENTE ===")

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
        }
    ]
)

print("Tabela cliente criada com sucesso")


print("\n=== INSERINDO CLIENTE ===")

cliente1 = inserir_em(
    banco,
    "cliente",
    [
        "Maria",
        20
    ]
)

print(cliente1.valores)


print("\n=== CRIANDO TABELA PEDIDO COM CHAVE ESTRANGEIRA ===")

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

print("Tabela pedido criada com sucesso")


print("\n=== INSERINDO PEDIDO COM FK VALIDA ===")

pedido1 = inserir_em(
    banco,
    "pedido",
    [
        "Pedido teste",
        1
    ]
)

print(pedido1.valores)


print("\n=== BUSCANDO REGISTROS NA ARVORE ===")

cliente_encontrado = (
    banco
    .buscar_tabela("cliente")
    .arvore
    .buscar(1)
)

pedido_encontrado = (
    banco
    .buscar_tabela("pedido")
    .arvore
    .buscar(1)
)

print(cliente_encontrado.valores)
print(pedido_encontrado.valores)


print("\n=== TESTANDO FK INEXISTENTE ===")

try:
    inserir_em(
        banco,
        "pedido",
        [
            "Pedido invalido",
            50
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO TIPO INVALIDO ===")

try:
    inserir_em(
        banco,
        "cliente",
        [
            "Joao",
            "25"
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO QUANTIDADE DE VALORES ===")

try:
    inserir_em(
        banco,
        "cliente",
        [
            "Joao"
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO VALOR NULO ===")

try:
    inserir_em(
        banco,
        "cliente",
        [
            None,
            25
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO APAGAR TABELA COM REGISTROS ===")

try:
    apagar_tabela(
        banco,
        "cliente"
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO CRIAR FK PARA TABELA INEXISTENTE ===")

try:
    criar_tabela(
        banco,
        "compra",
        [
            {
                "nome": "idProduto",
                "tipo": "INTEIRO",
                "chave_estrangeira": "produto"
            }
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO TABELA DUPLICADA ===")

try:
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

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO COLUNA DUPLICADA ===")

try:
    criar_tabela(
        banco,
        "teste_coluna",
        [
            {
                "nome": "nome",
                "tipo": "TEXTO"
            },
            {
                "nome": "nome",
                "tipo": "TEXTO"
            }
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO COLUNA ID ===")

try:
    criar_tabela(
        banco,
        "teste_id",
        [
            {
                "nome": "id",
                "tipo": "INTEIRO"
            }
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO TIPO DE DADO INVALIDO ===")

try:
    criar_tabela(
        banco,
        "teste_tipo",
        [
            {
                "nome": "valor",
                "tipo": "REAL"
            }
        ]
    )

except ErroIFFARQL as erro:
    print("Erro esperado:", erro)


print("\n=== TESTANDO PROXIMO ID ===")

cliente2 = inserir_em(
    banco,
    "cliente",
    [
        "Carlos",
        30
    ]
)

cliente3 = inserir_em(
    banco,
    "cliente",
    [
        "Ana",
        22
    ]
)

print("ID cliente 1:", cliente1.id)
print("ID cliente 2:", cliente2.id)
print("ID cliente 3:", cliente3.id)

tabela_cliente = banco.buscar_tabela("cliente")

print("Próximo id:", tabela_cliente.proximo_id)


print("\n=== TESTES FINALIZADOS ===")