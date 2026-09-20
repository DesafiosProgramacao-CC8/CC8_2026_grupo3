import os
from pathlib import Path
import subprocess
import sys
import tempfile

from persistencia import carregar_banco


projeto = Path(__file__).resolve().parents[1]
programa = projeto / "main.py"
ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")


def executar(argumentos, entrada=""):
    return subprocess.run(
        [sys.executable, "-B", str(programa), *map(str, argumentos)],
        input=entrada, text=True, encoding="utf-8", capture_output=True,
        env=ambiente, timeout=30,
    )


with tempfile.TemporaryDirectory(prefix="iffarql-terminal-") as pasta:
    pasta = Path(pasta)
    for nome in ("comandos.txt", "carregar.txt", "erros.txt"):
        (pasta / nome).write_bytes((projeto / "exemplos" / nome).read_bytes())

    cache = pasta / "cache.json"
    resultado = executar(["--arquivo", pasta / "comandos.txt", "--cache", cache])
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "Adao Silva" in resultado.stdout and "'id': 4" in resultado.stdout
    assert "Traceback" not in resultado.stderr
    salvo = pasta / "banco_exemplo.json"
    assert carregar_banco(salvo).buscar_tabela("cliente").proximo_id == 5

    recarregado = executar(["--arquivo", pasta / "carregar.txt", "--cache", pasta / "outro_cache.json"])
    assert recarregado.returncode == 0, recarregado.stdout + recarregado.stderr
    assert "Carlos" in recarregado.stdout and "Primeiro pedido" in recarregado.stdout

    erros = executar(["--arquivo", pasta / "erros.txt", "--cache", pasta / "cache_erros.json"])
    assert erros.returncode == 1, erros.stdout + erros.stderr
    for numero in (3, 4, 5, 6):
        assert f"linha {numero}:" in erros.stdout
    assert "'idade': 20" in erros.stdout and "'id': 2" in erros.stdout
    assert "Traceback" not in erros.stderr

    interativo = executar(
        ["--banco", salvo],
        '\nCOMANDO_INVALIDO\nINSERIREM cliente VALOR("Depois" 1.80 "01/01/2000" 4 False)\nSAIR\n',
    )
    assert interativo.returncode == 0, interativo.stdout + interativo.stderr
    assert "Comando desconhecido" in interativo.stdout
    assert "id 5" in interativo.stdout
    assert carregar_banco(salvo).buscar_tabela("cliente").proximo_id == 6

    inexistente = executar(["--banco", pasta / "nao_existe.json"])
    assert inexistente.returncode == 1 and "Erro:" in inexistente.stdout
    fim_de_entrada = executar(["--cache", pasta / "cache_vazio.json"])
    assert fim_de_entrada.returncode == 0 and "Sessão encerrada" in fim_de_entrada.stdout

print("Terminal: exemplos, erros por linha, reinício, autosave, entrada interativa e EOF passaram.")
