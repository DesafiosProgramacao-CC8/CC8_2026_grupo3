from erros import ErroIFFARQL
from token import Token
from tokenizador import converter_valor, tokenizar


casos_validos = [
    ('"Maria Silva"', "Maria Silva", True),
    ('"20"', "20", True),
    ("20", 20, False),
    ("20.0", 20.0, False),
    ("True", True, False),
    ("False", False, False),
    ('"True"', "True", True),
    ('"20/10/2010"', "20/10/2010", True),
    ('“Nome Sobrenome”', "Nome Sobrenome", True),
    ('“20/10/2010”', "20/10/2010", True),
    ('""', "", True),
    ('  " Maria Silva "  ', " Maria Silva ", True),
    ('"ONDE, COM >= +"', "ONDE, COM >= +", True),
    (" 20 ", 20, False),
    ("0", 0, False),
    ("-20", -20, False),
    ("+20", 20, False),
    ("-0.5", -0.5, False),
    ("+20.0", 20.0, False),
]

for entrada, valor_esperado, aspas_esperadas in casos_validos:
    token = converter_valor(entrada)
    assert isinstance(token, Token), repr(entrada)
    assert token.valor == valor_esperado, repr(entrada)
    # Igualdade sozinha não distingue 20 de 20.0 nem True de 1.
    assert type(token.valor) is type(valor_esperado), repr(entrada)
    assert token.com_aspas is aspas_esperadas, repr(entrada)


casos_invalidos = [
    "",
    "   ",
    '"',
    '"Maria',
    'Maria"',
    '"Maria" "Silva"',
    '“Maria"',
    '"Maria”',
    "Maria Silva",
    "true",
    "false",
    "None",
    "20/10/2010",
    "20,5",
    "1.2.3",
    "1_000",
    "1e3",
    "NaN",
    "inf",
    "+",
    "--20",
    "9" * 400 + ".0",
    None,
    20,
]

for entrada in casos_invalidos:
    try:
        converter_valor(entrada)
    except ErroIFFARQL:
        pass
    else:
        raise AssertionError(f"Era esperado ErroIFFARQL para {entrada!r}.")

print(
    f"Conversão de valores: {len(casos_validos)} casos válidos e "
    f"{len(casos_invalidos)} casos inválidos passaram."
)


comandos_validos = [
    ("MOSTRADADOSDE cliente", ["MOSTRADADOSDE", "cliente"]),
    (
        "MOSTRADADOSDE cliente ONDE idade>=18",
        ["MOSTRADADOSDE", "cliente", "ONDE", "idade", ">=", "18"],
    ),
    (
        'nome=="Maria Silva"',
        ["nome", "==", '"Maria Silva"'],
    ),
    (
        '("ONDE, COM >= +",20,20.0,True);',
        ["(", '"ONDE, COM >= +"', ",", "20", ",", "20.0", ",", "True", ")", ";"],
    ),
    (
        "idade=idade-3",
        ["idade", "=", "idade", "-", "3"],
    ),
    (
        "idade>=-18",
        ["idade", ">=", "-", "18"],
    ),
    (
        "saldo=saldo+20.0*2/4",
        ["saldo", "=", "saldo", "+", "20.0", "*", "2", "/", "4"],
    ),
    (
        "< <= > >= == <>",
        ["<", "<=", ">", ">=", "==", "<>"],
    ),
    (
        ' \t" Maria Silva "\t""  ',
        ['" Maria Silva "', '""'],
    ),
    (
        '"20/10/2010"',
        ['"20/10/2010"'],
    ),
    (
        'nome==“Nome Sobrenome”',
        ["nome", "==", '“Nome Sobrenome”'],
    ),
    (
        r'CARREGARIFFARQL "C:\Meus arquivos\comandos.txt"',
        ["CARREGARIFFARQL", r'"C:\Meus arquivos\comandos.txt"'],
    ),
]

for comando, partes_esperadas in comandos_validos:
    assert tokenizar(comando) == partes_esperadas, repr(comando)


comandos_invalidos = [
    "",
    " \t ",
    None,
    '"',
    'nome == "Maria Silva',
    '"Maria"Silva',
    'Maria" Silva"',
    '"Maria""Silva"',
    'nome == “Maria',
]

for comando in comandos_invalidos:
    try:
        tokenizar(comando)
    except ErroIFFARQL:
        pass
    else:
        raise AssertionError(f"Era esperado ErroIFFARQL para {comando!r}.")


# Verifica a passagem do comando textual para os valores usados nas operações.
partes = tokenizar('"Maria Silva" "20" 20 20.0 True "20/10/2010"')
tokens = [converter_valor(parte) for parte in partes]
assert [type(token.valor) for token in tokens] == [str, str, int, float, bool, str]
assert [token.com_aspas for token in tokens] == [True, True, False, False, False, True]

print(
    f"Separação de comandos: {len(comandos_validos)} casos válidos e "
    f"{len(comandos_invalidos)} casos inválidos passaram."
)
print("Integração entre tokenizar e converter_valor passou.")
