from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile

from erros import ErroIFFARQL
from interpretador import Interpretador
import interpretador
from persistencia import banco_para_dict, carregar_banco
import persistencia


def esperar_erro(acao):
    try:
        acao()
    except ErroIFFARQL:
        return
    raise AssertionError("Era esperado ErroIFFARQL.")


with tempfile.TemporaryDirectory(prefix="iffarql-interpretador-") as pasta:
    pasta = Path(pasta)
    cache = pasta / "cache.json"
    sessao = Interpretador(arquivo_cache=cache)
    executar = sessao.executar_comando
    executar("CRIATABELA cliente (nome TEXTO idade INTEIRO saldo DECIMAL ativo BOOLEANO cadastro DATA)")
    executar("CRIATABELA pedido (descricao TEXTO idCliente INTEIRO CHAVESTRANGEIRA cliente)")
    executar('INSERIREM cliente VALOR("Adão Silva" 20 20.0 True "28/02/2028")')
    executar('INSERIREM cliente VALOR("Ana" 17 30.0 False "01/01/2026")')
    executar('INSERIREM cliente VALOR("Carlos" 30 50.0 True "01/01/2025")')
    executar('INSERIREM pedido VALOR("Descrição" 1)')
    assert sessao.banco.buscar_tabela("cliente").arvore.buscar(1).valores["nome"] == "Adao Silva"
    assert banco_para_dict(carregar_banco(cache)) == banco_para_dict(sessao.banco)

    saida = StringIO()
    arquivo_antes_consulta = cache.read_bytes()
    with redirect_stdout(saida):
        executar('MOSTRADADOSDE cliente ONDE nome=="Adão Silva"')
    assert "Adao Silva" in saida.getvalue() and "Ana" not in saida.getvalue()
    assert cache.read_bytes() == arquivo_antes_consulta

    executar("ATUALIZATABELA cliente COM idade=21 ONDE id==1")
    executar('ATUALIZATABELA cliente COM cadastro=cadastro+1 COM nome=nome+" Júnior" ONDE id==1')
    registro = sessao.banco.buscar_tabela("cliente").arvore.buscar(1)
    assert registro.valores["nome"] == "Adao Silva Junior"
    assert registro.valores["cadastro"] == "29/02/2028"
    executar("ATUALIZATABELA cliente COM saldo=saldo-5.0 ONDE id==1")
    assert sessao.banco.buscar_tabela("cliente").arvore.buscar(1).valores["saldo"] == 15.0

    # Tanto a memória quanto o arquivo devem ficar intactos em cada erro.
    falhas = [
        "CRIATABELA cliente (n INTEIRO)",
        "CRIATABELA invalida (nome TEXTO id INTEIRO)",
        "CRIATABELA invalida (cliente INTEIRO CHAVESTRANGEIRA ausente)",
        "ATUALIZATABELA cliente COM idade=idade+10 COM saldo=saldo/0.0",
        "ATUALIZATABELA cliente COM idade=idade+1.0",
        "ATUALIZATABELA cliente COM id=10",
        "ATUALIZATABELA pedido COM idCliente=idCliente+99",
        "APAGADADOSDE cliente ONDE id==1",
        "APAGATABELA cliente",
        'INSERIREM cliente VALOR("Nome" "20" 20.0 True "01/01/2026")',
        "INSERIREM cliente VALOR(20)",
        "MOSTRADADOSDE cliente ONDE idade==20 ONDE id==1",
        "MOSTRADADOSDE cliente ONDE ativo>True",
        "ATUALIZATABELA cliente COM idade=22 COM saldo=0.0 sobra",
    ]
    for comando in falhas:
        memoria = banco_para_dict(sessao.banco)
        disco = cache.read_bytes()
        esperar_erro(lambda: executar(comando))
        assert banco_para_dict(sessao.banco) == memoria, comando
        assert cache.read_bytes() == disco, comando

    executar("CRIATABELA vazia (idade INTEIRO)")
    esperar_erro(lambda: executar("MOSTRADADOSDE vazia ONDE ausente==1"))
    esperar_erro(lambda: executar('APAGADADOSDE vazia ONDE idade=="1"'))
    executar("APAGATABELA vazia")

    # Simula uma falha no último passo da gravação após a operação em memória.
    memoria = banco_para_dict(sessao.banco)
    disco = cache.read_bytes()
    substituir_original = persistencia.os.replace

    def falhar_substituicao(origem, destino):
        raise OSError("Falha de disco simulada.")

    persistencia.os.replace = falhar_substituicao
    try:
        esperar_erro(lambda: executar("ATUALIZATABELA cliente COM idade=99"))
    finally:
        persistencia.os.replace = substituir_original
    assert banco_para_dict(sessao.banco) == memoria
    assert cache.read_bytes() == disco

    inserir_original = interpretador.inserir_em

    def inserir_com_falha(banco, nome_tabela, valores):
        banco.buscar_tabela(nome_tabela).gerar_id()
        raise RuntimeError("Falha inesperada depois de modificar a cópia.")

    interpretador.inserir_em = inserir_com_falha
    try:
        esperar_erro(lambda: executar('INSERIREM cliente VALOR("Falha" 20 1.0 True "01/01/2026")'))
    finally:
        interpretador.inserir_em = inserir_original
    assert banco_para_dict(sessao.banco) == memoria
    assert cache.read_bytes() == disco

    executar("APAGADADOSDE cliente ONDE id==3")
    salvo = pasta / "banco definitivo.json"
    executar(f'SALVARBD "{salvo}"')
    assert sessao.arquivo_ativo == salvo
    cache_antes = cache.read_bytes()
    executar('INSERIREM cliente VALOR("Nova" 31 1.0 False "01/01/2026")')
    assert sessao.banco.buscar_tabela("cliente").arvore.buscar(4) is not None
    assert cache.read_bytes() == cache_antes
    assert carregar_banco(salvo).buscar_tabela("cliente").proximo_id == 5
    esperar_erro(lambda: executar(f'CARREGARBD "{salvo}"'))
    esperar_erro(lambda: executar(f'SALVARBD "{pasta / "ausente" / "banco.json"}"'))
    assert sessao.arquivo_ativo == salvo

    nova = Interpretador(arquivo_cache=pasta / "cache_novo.json")
    esperar_erro(lambda: nova.executar_comando(f'CARREGARBD "{pasta / "ausente.json"}"'))
    assert nova.banco.tabelas == {} and nova.arquivo_ativo is None
    nova.executar_comando(f'CARREGARBD "{salvo}"')
    nova.executar_comando('INSERIREM cliente VALOR("Depois" 20 1.0 True "01/01/2026")')
    assert carregar_banco(salvo).buscar_tabela("cliente").arvore.buscar(5) is not None

    sem_pasta = Interpretador(arquivo_cache=pasta / "inexistente" / "cache.json")
    esperar_erro(lambda: sem_pasta.executar_comando("CRIATABELA t(n INTEIRO)"))
    assert sem_pasta.banco.tabelas == {}

    # O erro de uma linha não desfaz as linhas válidas nem impede as seguintes.
    roteiro = pasta / "comandos.txt"
    roteiro.write_text(
        'CRIATABELA t (nome TEXTO n INTEIRO)\n'
        'INSERIREM t VALOR("Primeiro" 1)\n'
        'INSERIREM t VALOR("Erro" "2")\n'
        '\n'
        'INSERIREM t VALOR("Segundo" 2)\n'
        'ATUALIZATABELA t COM n=n+1 COM n=n/0\n'
        'SALVARBD resultado.json\n', encoding="utf-8-sig",
    )
    arquivo_sessao = Interpretador(arquivo_cache=pasta / "cache_txt.json")
    resultado = arquivo_sessao.executar_comando(f'CARREGARIFFARQL "{roteiro}"')
    assert len(resultado.erros) == 2
    assert "linha 3" in resultado.erros[0] and "linha 6" in resultado.erros[1]
    tabela = arquivo_sessao.banco.buscar_tabela("t")
    assert [registro.valores["n"] for registro in tabela.arvore.listar_registros()] == [1, 2]
    assert tabela.proximo_id == 3
    assert banco_para_dict(carregar_banco(pasta / "resultado.json")) == banco_para_dict(arquivo_sessao.banco)

    subpasta = pasta / "subpasta"
    subpasta.mkdir()
    (subpasta / "filho.txt").write_text('INSERIREM t VALOR("Terceiro" 3)\n', encoding="utf-8")
    pai = pasta / "pai.txt"
    pai.write_text("CARREGARIFFARQL subpasta/filho.txt\nCARREGARIFFARQL pai.txt\n", encoding="utf-8")
    resultado = arquivo_sessao.executar_comando(f'CARREGARIFFARQL "{pai}"')
    assert len(resultado.erros) == 1 and "linha 2" in resultado.erros[0]
    assert arquivo_sessao.banco.buscar_tabela("t").arvore.buscar(3).valores["n"] == 3
    assert arquivo_sessao._arquivos_em_execucao == []
    esperar_erro(lambda: arquivo_sessao.executar_comando(f'CARREGARIFFARQL "{salvo}"'))

print("Interpretador: comandos, consultas, autosave, rollback, FKs, IDs e arquivos TXT passaram.")
