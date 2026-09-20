import json
import math
import os
from pathlib import Path
import tempfile

from banco import BancoDados
from coluna import Coluna
from erros import ErroIFFARQL
from operacoes import criar_tipo
from registro import Registro
from tabela import Tabela
from tipos.booleano import Booleano
from tipos.data import Data
from tipos.decimal import Decimal
from tipos.inteiro import Inteiro
from tipos.texto import Texto


TIPOS = {
    Inteiro: "INTEIRO", Decimal: "DECIMAL", Booleano: "BOOLEANO",
    Texto: "TEXTO", Data: "DATA",
}


def exigir(condicao, mensagem):
    if not condicao:
        raise ErroIFFARQL(f"Banco inválido: {mensagem}")


def banco_para_dict(banco):
    """Produz uma fotografia dos dados, sem referências aos registros originais."""
    tabelas = []
    for tabela in banco.tabelas.values():
        colunas = []
        for coluna in tabela.colunas[1:]:
            exigir(type(coluna.tipo) in TIPOS, "tipo de coluna desconhecido.")
            colunas.append({
                "nome": coluna.nome,
                "tipo": TIPOS[type(coluna.tipo)],
                "chave_estrangeira": coluna.chave_estrangeira,
            })
        tabelas.append({
            "nome": tabela.nome,
            "colunas": colunas,
            "proximo_id": tabela.proximo_id,
            "registros": [dict(registro.valores) for registro in tabela.arvore.listar_registros()],
        })
    return {"versao": 1, "tabelas": tabelas}


def _inserir_registros(tabela, registros, inicio, fim):
    # Inserir a mediana primeiro evita reconstruir uma árvore em forma de lista.
    if inicio >= fim:
        return
    meio = (inicio + fim) // 2
    valores = registros[meio]
    registro = Registro(valores["id"], dict(valores))
    tabela.arvore.inserir(registro.id, registro)
    _inserir_registros(tabela, registros, inicio, meio)
    _inserir_registros(tabela, registros, meio + 1, fim)


def banco_de_dict(dados):
    """Reconstrói e valida tudo antes de devolver um banco utilizável."""
    exigir(isinstance(dados, dict), "o conteúdo deve ser um objeto JSON.")
    exigir(set(dados) == {"versao", "tabelas"}, "estrutura ou versão ausente.")
    exigir(type(dados["versao"]) is int and dados["versao"] == 1, "versão não suportada.")
    exigir(isinstance(dados["tabelas"], list), "tabelas deve ser uma lista.")
    banco = BancoDados()

    for dados_tabela in dados["tabelas"]:
        exigir(isinstance(dados_tabela, dict), "definição de tabela inválida.")
        exigir(set(dados_tabela) == {"nome", "colunas", "proximo_id", "registros"},
               "campos da tabela incompletos ou desconhecidos.")
        nome = dados_tabela["nome"]
        exigir(isinstance(nome, str) and bool(nome.strip()), "nome de tabela inválido.")
        exigir(isinstance(dados_tabela["colunas"], list), "colunas deve ser uma lista.")
        tabela = Tabela(nome)
        banco.adicionar_tabela(tabela)

        for dados_coluna in dados_tabela["colunas"]:
            exigir(isinstance(dados_coluna, dict), "coluna inválida.")
            exigir(set(dados_coluna) == {"nome", "tipo", "chave_estrangeira"},
                   "definição de coluna incompleta ou desconhecida.")
            nome_coluna = dados_coluna["nome"]
            exigir(isinstance(nome_coluna, str) and bool(nome_coluna.strip()),
                   "nome de coluna inválido.")
            tipo = criar_tipo(dados_coluna["tipo"])
            referencia = dados_coluna["chave_estrangeira"]
            exigir(referencia is None or (isinstance(referencia, str) and bool(referencia)),
                   "referência de chave estrangeira inválida.")
            exigir(referencia is None or isinstance(tipo, Inteiro), "FK deve ser INTEIRO.")
            tabela.adicionar_coluna(Coluna(nome_coluna, tipo, referencia))

        registros = dados_tabela["registros"]
        exigir(isinstance(registros, list), "registros deve ser uma lista.")
        nomes_colunas = {coluna.nome for coluna in tabela.colunas}
        ids = set()
        for valores in registros:
            exigir(isinstance(valores, dict) and set(valores) == nomes_colunas,
                   f"campos do registro incompatíveis com a tabela '{nome}'.")
            id_registro = valores["id"]
            exigir(type(id_registro) is int and id_registro > 0, "id deve ser inteiro positivo.")
            exigir(id_registro not in ids, "id duplicado.")
            ids.add(id_registro)
            for coluna in tabela.colunas:
                valor = valores[coluna.nome]
                exigir(coluna.validar_valor(valor), f"valor inválido em '{nome}.{coluna.nome}'.")
                if isinstance(valor, float):
                    exigir(math.isfinite(valor), "valor decimal não finito.")

        proximo_id = dados_tabela["proximo_id"]
        exigir(type(proximo_id) is int and proximo_id > max(ids, default=0),
               "proximo_id deve ser maior que todos os IDs existentes.")
        tabela.definir_proximo_id(proximo_id)
        ordenados = sorted(registros, key=lambda valores: valores["id"])
        _inserir_registros(tabela, ordenados, 0, len(ordenados))

    # Todas as tabelas precisam existir antes de conferir as referências.
    for tabela in banco.tabelas.values():
        for coluna in tabela.colunas:
            if coluna.chave_estrangeira is None:
                continue
            referencia = banco.buscar_tabela(coluna.chave_estrangeira)
            for registro in tabela.arvore.listar_registros():
                exigir(referencia.arvore.buscar(registro.valores[coluna.nome]) is not None,
                       f"chave estrangeira inexistente em '{tabela.nome}.{coluna.nome}'.")
    return banco


def _objeto_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        exigir(chave not in objeto, f"campo JSON repetido: '{chave}'.")
        objeto[chave] = valor
    return objeto


def carregar_banco(caminho):
    try:
        with Path(caminho).open("r", encoding="utf-8-sig") as arquivo:
            dados = json.load(arquivo, object_pairs_hook=_objeto_sem_duplicatas)
        return banco_de_dict(dados)
    except ErroIFFARQL:
        raise
    except (OSError, ValueError, TypeError, RecursionError) as erro:
        raise ErroIFFARQL(f"Não foi possível carregar '{caminho}': {erro}") from erro


def salvar_banco(banco, caminho):
    """Substitui o destino somente depois de terminar a gravação temporária."""
    temporario = None
    try:
        dados = banco_para_dict(banco)
        banco_de_dict(dados)
        destino = Path(caminho).resolve()
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destino.parent,
            prefix=f".{destino.name}.", suffix=".tmp", delete=False,
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, destino)
    except ErroIFFARQL:
        raise
    except (OSError, ValueError, TypeError, RecursionError) as erro:
        raise ErroIFFARQL(f"Não foi possível salvar '{caminho}': {erro}") from erro
    finally:
        if temporario is not None:
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass
