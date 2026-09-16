from tabela import Tabela
from coluna import Coluna
from registro import Registro
from token import Token

from tipos.inteiro import Inteiro
from tipos.decimal import Decimal
from tipos.texto import Texto
from tipos.booleano import Booleano
from tipos.data import Data

from condicoes import avaliar_condicao

from erros import ErroIFFARQL


tabela = Tabela("pessoa")

tabela.adicionar_coluna(
    Coluna("nome", Texto())
)

tabela.adicionar_coluna(
    Coluna("idade", Inteiro())
)

tabela.adicionar_coluna(
    Coluna("altura", Decimal())
)

tabela.adicionar_coluna(
    Coluna("ativo", Booleano())
)

tabela.adicionar_coluna(
    Coluna("nascimento", Data())
)


registro = Registro(
    1,
    {
        "nome": "Maria",
        "idade": 25,
        "altura": 1.70,
        "ativo": True,
        "nascimento": "29/02/2000"
    }
)

# Teste com operadores
print(
    avaliar_condicao(
        tabela,
        registro,
        "idade",
        ">=",
        Token(18, False)
    )
)

print(
    avaliar_condicao(
        tabela,
        registro,
        "idade",
        "<",
        Token(18, False)
    )
)

# Teste com TEXTO
print(
    avaliar_condicao(
        tabela,
        registro,
        "nome",
        "==",
        Token("Maria", True)
    )
)


# Teste com ID
print(
    avaliar_condicao(
        tabela,
        registro,
        "id",
        "==",
        Token(1, False)
    )
)

# Teste com DATA
print( 
    avaliar_condicao(
        tabela,
        registro,
        "nascimento",
        ">",
        Token("01/01/1999", True)
    )
)


# Teste de erro
print("\nTESTE 1 - INTEIRO COM ASPAS")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "idade",
            "==",
            Token("25", True)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 2 - OPERADOR INVALIDO PARA BOOLEANO")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "ativo",
            ">",
            Token(False, False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 3 - DATA SEM ASPAS")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "nascimento",
            ">=",
            Token("01/01/2000", False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 4 - COLUNA INEXISTENTE")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "salario",
            ">",
            Token(5000, False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 5 - OPERADOR INEXISTENTE")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "idade",
            "???",
            Token(18, False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 6 - DECIMAL VALIDO")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "altura",
            ">=",
            Token(1.60, False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)

print("\nTESTE 7 - BOOLEANO VALIDO")
try:
    print(
        avaliar_condicao(
            tabela,
            registro,
            "ativo",
            "==",
            Token(True, False)
        )
    )
except ErroIFFARQL as erro:
    print(erro)