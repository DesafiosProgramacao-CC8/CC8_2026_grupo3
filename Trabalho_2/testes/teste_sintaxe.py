from erros import ErroIFFARQL
from sintaxe import analisar_comando


criacao = analisar_comando(
    "CRIATABELA tabela_exemplo ( nome TEXTO altura DECIMAL data_nascimento DATA tickets INTEIRO )"
)
assert criacao["tabela"] == "tabela_exemplo"
assert [coluna["tipo"] for coluna in criacao["colunas"]] == ["TEXTO", "DECIMAL", "DATA", "INTEIRO"]
referencia = analisar_comando(
    "CRIATABELA tabela_exemplo2 ( cpf TEXTO endereco TEXTO idCliente INTEIRO CHAVESTRANGEIRA tabela_exemplo )"
)
assert referencia["colunas"][-1]["chave_estrangeira"] == "tabela_exemplo"

insercao = analisar_comando('INSERIREM tabela_exemplo VALOR ( “Nome Sobrenome” 1.80 “20/10/2010” 20 )')
assert [token.valor for token in insercao["valores"]] == ["Nome Sobrenome", 1.8, "20/10/2010", 20]
assert [type(token.valor) for token in insercao["valores"]] == [str, float, str, int]
assert analisar_comando("INSERIREM t VALOR(-3 -1.5 True)")["valores"][0].valor == -3

simples = analisar_comando("ATUALIZATABELA tabela_exemplo COM tickets = 30 ONDE altura > 1.90")
assert simples["atualizacoes"][0]["operador"] is None
assert simples["atualizacoes"][0]["token"].valor == 30
assert simples["condicao"][:2] == ("altura", ">")
multiplos = analisar_comando(
    'ATUALIZATABELA tabela_exemplo COM tickets=tickets+3 COM altura=altura-0.15 ONDE data_nascimento==“15/05/2008”'
)
assert [item["operador"] for item in multiplos["atualizacoes"]] == ["+", "-"]
assert multiplos["condicao"][2].valor == "15/05/2008"
negativo = analisar_comando("ATUALIZATABELA t COM n=n+-3 ONDE n>=-10")
assert negativo["atualizacoes"][0]["token"].valor == -3
assert negativo["condicao"][2].valor == -10
booleano = analisar_comando("ATUALIZATABELA t COM True=True")
assert booleano["atualizacoes"][0]["token"].valor is True

for nome in ("MOSTRADADOSDE", "APAGADADOSDE"):
    assert analisar_comando(f"{nome} t")["condicao"] == (None, None, None)
    for operador in ("<", "<=", ">", ">=", "==", "<>"):
        assert analisar_comando(f"{nome} t ONDE n{operador}20")["condicao"][1] == operador

assert analisar_comando("APAGATABELA t") == {"comando": "APAGATABELA", "tabela": "t"}
for nome in ("SALVARBD", "CARREGARBD", "CARREGARIFFARQL"):
    assert analisar_comando(f"{nome} pasta/meu-banco.json")["caminho"] == "pasta/meu-banco.json"
    assert analisar_comando(f'{nome} "C:\\Meus arquivos\\ação.txt"')["caminho"] == "C:\\Meus arquivos\\ação.txt"

invalidos = [
    "", "mostradadosde t", "COMANDO t", "CRIATABELA", "CRIATABELA t nome TEXTO",
    "CRIATABELA t (nome)", "CRIATABELA t (nome TEXTO", "CRIATABELA t(nome TEXTO) sobra",
    "CRIATABELA 1t (nome TEXTO)", "CRIATABELA t (nome TEXTO, idade INTEIRO)",
    "INSERIREM t (20)", "INSERIREM t VALOR(20", "INSERIREM t VALOR(20, 30)",
    'INSERIREM t VALOR("Maria)', "APAGATABELA t sobra", "MOSTRADADOSDE t ONDE",
    "MOSTRADADOSDE t ONDE idade=20", "MOSTRADADOSDE t ONDE idade==20 ONDE id==1",
    "ATUALIZATABELA t", "ATUALIZATABELA t COM idade 20", "ATUALIZATABELA t COM idade=",
    "ATUALIZATABELA t COM idade=idade+", "ATUALIZATABELA t COM idade=outra+1",
    "SALVARBD", 'SALVARBD ""', "CARREGARBD dois arquivos.json", 'SALVARBD "arquivo',
]
for comando in invalidos:
    try:
        analisar_comando(comando)
    except ErroIFFARQL:
        pass
    else:
        raise AssertionError(f"Sintaxe deveria falhar: {comando!r}")

print("Sintaxe: exemplos do enunciado, operadores, caminhos e comandos inválidos passaram.")
