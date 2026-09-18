from tipos.inteiro import Inteiro
from tipos.decimal import Decimal
from tipos.booleano import Booleano
from erros import ErroIFFARQL
from tipos.texto import Texto
from tipos.data import Data

inteiro = Inteiro()
decimal = Decimal()
booleano = Booleano()
texto = Texto()
data = Data()

print("=== TESTE 1 - SOMA DE INTEIROS ===")
print(
    inteiro.operar(
        20,
        "+",
        3
    )
)

print("\n=== TESTE 2 - SUBTRACAO DE INTEIROS ===")
print(
    inteiro.operar(
        20,
        "-",
        3
    )
)

print("\n=== TESTE 3 - MULTIPLICACAO DE INTEIROS ===")
print(
    inteiro.operar(
        20,
        "*",
        3
    )
)

print("\n=== TESTE 4 - DIVISAO DE INTEIROS ===")
print(
    inteiro.operar(
        20,
        "/",
        4
    )
)

print("\n=== TESTE 5 - SOMA DE DECIMAIS ===")
print(
    decimal.operar(
        1.5,
        "+",
        0.5
    )
)

print("\n=== TESTE 6 - SUBTRACAO DE DECIMAIS ===")
print(
    decimal.operar(
        1.80,
        "-",
        0.15
    )
)

print("\n=== TESTE 7 - MISTURA DE TIPOS ===")
try:
    inteiro.operar(
        20,
        "+",
        3.5
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 8 - DIVISAO POR ZERO ===")
try:
    decimal.operar(
        10.0,
        "/",
        0.0
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 9 - OPERACAO COM BOOLEANO ===")
try:
    booleano.operar(
        True,
        "+",
        False
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 10 - CONCATENACAO DE TEXTO ===")
print(
    texto.operar(
        "Maria",
        "+",
        " Silva"
    )
)

print("\n=== TESTE 11 - OPERADOR INVALIDO PARA TEXTO ===")
try:
    texto.operar(
        "Maria",
        "-",
        "Maria"
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 12 - SOMA DE DIAS EM DATA ===")
print(
    data.operar(
        "01/02/2023",
        "+",
        123
    )
)

print("\n=== TESTE 13 - SUBTRACAO DE DIAS EM DATA ===")
print(
    data.operar(
        "10/01/2026",
        "-",
        10
    )
)

print("\n=== TESTE 14 - DATA COM DECIMAL ===")
try:
    data.operar(
        "01/02/2023",
        "+",
        10.5
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 15 - OPERADOR INVALIDO PARA DATA ===")
try:
    data.operar(
        "01/02/2023",
        "*",
        10
    )
except ErroIFFARQL as erro:
    print("Erro esperado:", erro)

print("\n=== TESTE 16 - ANO BISSEXTO ===")
print(
    data.operar(
        "28/02/2028",
        "+",
        1
    )
)