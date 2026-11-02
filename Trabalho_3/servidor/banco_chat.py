from pathlib import Path

from ..iffarql.banco import BancoDados
from ..iffarql.consultas import apagar_dados, atualizar_multiplos
from ..iffarql.erros import ErroIFFARQL
from ..iffarql.operacoes import criar_tabela, inserir_em
from ..iffarql.persistencia import (
    banco_de_dict, banco_para_dict, carregar_banco, salvar_banco,
)
from ..iffarql.sintaxe import analisar_comando
from ..iffarql.token import Token


PASTA_BANCO = Path(__file__).resolve().parents[1] / "banco"
ARQUIVO_BANCO = PASTA_BANCO / "iffarchat.json"


class BancoChat:
    def __init__(self, caminho=ARQUIVO_BANCO):
        self.caminho = Path(caminho)
        self.alterado = False
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

        # Uso o script IFFARQL para montar as tabelas do chat
        modelo = BancoDados()
        script = (PASTA_BANCO / "estrutura.txt").read_text(encoding="utf-8")
        for linha in script.splitlines():
            if linha.strip():
                comando = analisar_comando(linha)
                criar_tabela(modelo, comando["tabela"], comando["colunas"])

        if self.caminho.exists():
            self.banco = carregar_banco(self.caminho)
            self._conferir_estrutura(modelo)
        else:
            self.banco = modelo
            salvar_banco(self.banco, self.caminho)

    def _conferir_estrutura(self, modelo):
        for nome, tabela in modelo.tabelas.items():
            existente = self.banco.buscar_tabela(nome)
            esperado = [(c.nome, type(c.tipo), c.chave_estrangeira) for c in tabela.colunas]
            recebido = [(c.nome, type(c.tipo), c.chave_estrangeira) for c in existente.colunas]
            if recebido != esperado:
                raise ErroIFFARQL(f"Estrutura incompatível na tabela {nome}")

    def executar(self, operacao, *argumentos):
        # Trabalho em uma cópia para não deixar uma alteração pela metade
        anterior = self.banco
        self.banco = banco_de_dict(banco_para_dict(anterior))
        self.alterado = False
        try:
            resultado = operacao(*argumentos)
            if self.alterado:
                salvar_banco(self.banco, self.caminho)
            return resultado
        except Exception:
            # Se der erro, volto para o banco que estava funcionando
            self.banco = anterior
            raise

    def listar(self, tabela):
        registros = self.banco.buscar_tabela(tabela).arvore.listar_registros()
        return [dict(registro.valores) for registro in registros]

    def buscar(self, tabela, id_registro):
        registro = self.banco.buscar_tabela(tabela).arvore.buscar(id_registro)
        return dict(registro.valores) if registro is not None else None

    def inserir(self, tabela, valores):
        # Passo os valores separados para preservar acentos e aspas nas mensagens
        tokens = [Token(valor, isinstance(valor, str)) for valor in valores]
        registro = inserir_em(self.banco, tabela, tokens)
        self.alterado = True
        return dict(registro.valores)

    def atualizar(self, tabela, id_registro, valores):
        atualizacoes = []
        for coluna, valor in valores.items():
            atualizacoes.append({
                "coluna": coluna,
                "token": Token(valor, isinstance(valor, str)),
            })
        atualizar_multiplos(
            self.banco, tabela, atualizacoes, "id", "==", Token(id_registro)
        )
        self.alterado = True

    def remover(self, tabela, id_registro):
        apagar_dados(self.banco, tabela, "id", "==", Token(id_registro))
        self.alterado = True
