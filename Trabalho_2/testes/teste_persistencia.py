from copy import deepcopy
from pathlib import Path
import tempfile

from banco import BancoDados
from erros import ErroIFFARQL
from operacoes import criar_tabela, inserir_em
import persistencia
from persistencia import banco_para_dict, banco_de_dict, carregar_banco, salvar_banco
from token import Token


def esperar_erro(acao):
    try:
        acao()
    except ErroIFFARQL:
        return
    raise AssertionError("Era esperado ErroIFFARQL.")


banco = BancoDados()
criar_tabela(banco, "cliente", [
    {"nome": "nome", "tipo": "TEXTO"},
    {"nome": "idade", "tipo": "INTEIRO"},
    {"nome": "saldo", "tipo": "DECIMAL"},
    {"nome": "ativo", "tipo": "BOOLEANO"},
    {"nome": "cadastro", "tipo": "DATA"},
])
criar_tabela(banco, "pedido", [{"nome": "cliente", "tipo": "INTEIRO", "chave_estrangeira": "cliente"}])
criar_tabela(banco, "vazia", [{"nome": "nome", "tipo": "TEXTO"}])
for nome in ("Maria", "Joao", "Ana"):
    inserir_em(banco, "cliente", [Token(nome, True), Token(20), Token(20.0), Token(True), Token("28/02/2028", True)])
inserir_em(banco, "pedido", [Token(1)])
banco.buscar_tabela("cliente").arvore.remover(3)
dados = banco_para_dict(banco)
assert dados["tabelas"][0]["proximo_id"] == 4

# A ordem das tabelas no arquivo não deve limitar a reconstrução das FKs.
invertido = deepcopy(dados)
invertido["tabelas"].reverse()
reconstruido = banco_de_dict(invertido)
assert reconstruido.buscar_tabela("pedido").arvore.buscar(1).valores["cliente"] == 1

with tempfile.TemporaryDirectory(prefix="iffarql-persistencia-") as pasta:
    pasta = Path(pasta)
    arquivo = pasta / "banco ação.json"
    salvar_banco(banco, arquivo)
    carregado = carregar_banco(arquivo)
    assert banco_para_dict(carregado) == dados
    valores = carregado.buscar_tabela("cliente").arvore.buscar(1).valores
    assert type(valores["idade"]) is int
    assert type(valores["saldo"]) is float
    assert type(valores["ativo"]) is bool
    assert carregado.buscar_tabela("vazia").arvore.esta_vazia()
    novo = inserir_em(carregado, "cliente", [Token("Carlos", True), Token(21), Token(5.0), Token(False), Token("01/01/2026", True)])
    assert novo.id == 4

    conteudo_anterior = arquivo.read_bytes()
    substituir_original = persistencia.os.replace

    def falhar_substituicao(origem, destino):
        raise OSError("Falha de gravação simulada.")

    persistencia.os.replace = falhar_substituicao
    try:
        esperar_erro(lambda: salvar_banco(carregado, arquivo))
    finally:
        persistencia.os.replace = substituir_original
    assert arquivo.read_bytes() == conteudo_anterior
    assert list(pasta.glob("*.tmp")) == []
    esperar_erro(lambda: salvar_banco(banco, pasta / "ausente" / "banco.json"))
    esperar_erro(lambda: carregar_banco(pasta / "ausente.json"))

    for texto in ("não é JSON", '{"versao":1,"versao":1,"tabelas":[]}', "[]"):
        invalido = pasta / "invalido.json"
        invalido.write_text(texto, encoding="utf-8")
        esperar_erro(lambda: carregar_banco(invalido))

mutacoes = [
    lambda d: d.update(versao=2),
    lambda d: d.update(versao=True),
    lambda d: d["tabelas"].append(deepcopy(d["tabelas"][0])),
    lambda d: d["tabelas"][0].update(proximo_id=2),
    lambda d: d["tabelas"][0].update(proximo_id=True),
    lambda d: d["tabelas"][0]["colunas"][0].update(tipo="INVALIDO"),
    lambda d: d["tabelas"][0]["registros"][0].update(id=True),
    lambda d: d["tabelas"][0]["registros"][0].update(idade="20"),
    lambda d: d["tabelas"][0]["registros"][0].update(saldo=float("nan")),
    lambda d: d["tabelas"][0]["registros"].append(deepcopy(d["tabelas"][0]["registros"][0])),
    lambda d: d["tabelas"][0]["registros"][0].pop("nome"),
    lambda d: d["tabelas"][1]["registros"][0].update(cliente=999),
    lambda d: d["tabelas"][1]["colunas"][0].update(chave_estrangeira="ausente"),
    lambda d: d["tabelas"][1]["colunas"][0].update(tipo="TEXTO"),
]
for mudar in mutacoes:
    invalido = deepcopy(dados)
    mudar(invalido)
    esperar_erro(lambda: banco_de_dict(invalido))
assert banco_para_dict(banco) == dados

# A reconstrução não insere 1.500 IDs em sequência numa árvore degenerada.
grande = {"versao": 1, "tabelas": [{
    "nome": "ids", "colunas": [], "proximo_id": 1501,
    "registros": [{"id": numero} for numero in range(1, 1501)],
}]}
assert banco_para_dict(banco_de_dict(grande)) == grande
print("Persistência: ida e volta, tipos, FKs, IDs, arquivo inválido e falha de gravação passaram.")
