from pathlib import Path

from banco import BancoDados
from condicoes import buscar_coluna, validar_operador, validar_token
from consultas import (
    mostrar_dados, apagar_dados, atualizar_dados,
    atualizar_com_operacao, atualizar_multiplos,
)
from erros import ErroIFFARQL
from operacoes import criar_tabela, apagar_tabela, inserir_em
from persistencia import banco_para_dict, banco_de_dict, salvar_banco, carregar_banco
from sintaxe import analisar_comando
from token import Token
from tipos.texto import Texto


CACHE_PADRAO = Path(__file__).resolve().parent / ".iffarql_cache.json"


class ResultadoComando:
    def __init__(self, mensagem, erros=None):
        self.mensagem = mensagem
        self.erros = erros if erros is not None else []


class Interpretador:
    """Mantém o banco, o arquivo ativo e a execução das transações da sessão."""

    def __init__(self, banco=None, arquivo_cache=None):
        self.banco = banco if banco is not None else BancoDados()
        self.arquivo_cache = Path(arquivo_cache) if arquivo_cache is not None else CACHE_PADRAO
        self.arquivo_ativo = None
        self._arquivos_em_execucao = []

    def executar_comando(self, texto):
        try:
            comando = analisar_comando(texto)
            nome = comando["comando"]

            if nome == "SALVARBD":
                caminho = self._resolver_caminho(comando["caminho"])
                salvar_banco(self.banco, caminho)
                self.arquivo_ativo = caminho
                return ResultadoComando(f"Banco salvo em '{caminho}'.")

            if nome == "CARREGARBD":
                if self.banco.tabelas:
                    raise ErroIFFARQL("CARREGARBD exige um banco sem tabelas.")
                caminho = self._resolver_caminho(comando["caminho"])
                carregado = carregar_banco(caminho)
                self.banco.tabelas = carregado.tabelas
                self.arquivo_ativo = caminho
                return ResultadoComando(f"Banco carregado de '{caminho}'.")

            if nome == "CARREGARIFFARQL":
                return self._carregar_comandos(self._resolver_caminho(comando["caminho"]))

            if nome == "MOSTRADADOSDE":
                self._preparar_parametros(self.banco, comando)
                mostrar_dados(self.banco, comando["tabela"], *comando["condicao"])
                return ResultadoComando("")

            # A cópia funciona como área de trabalho da transação.
            copia = banco_de_dict(banco_para_dict(self.banco))
            self._preparar_parametros(copia, comando)
            mensagem = self._alterar_banco(copia, comando)
            destino = self.arquivo_ativo if self.arquivo_ativo is not None else self.arquivo_cache
            salvar_banco(copia, destino)
            # Só confirma em memória depois de persistir com sucesso.
            self.banco.tabelas = copia.tabelas
            return ResultadoComando(mensagem)
        except ErroIFFARQL:
            raise
        except Exception as erro:
            # Falhas inesperadas das operações não publicam a cópia da transação.
            raise ErroIFFARQL(
                f"Não foi possível executar o comando ({type(erro).__name__}): {erro}"
            ) from erro

    def _preparar_token(self, coluna, token):
        if isinstance(coluna.tipo, Texto) and isinstance(token.valor, str):
            # Reutiliza a normalização já implementada pela Pessoa 1.
            valor = coluna.tipo.remover_acentos(token.valor)
            return Token(valor, token.com_aspas)
        return token

    def _preparar_parametros(self, banco, comando):
        nome = comando["comando"]
        if nome == "CRIATABELA":
            return
        tabela = banco.buscar_tabela(comando["tabela"])

        if "condicao" in comando:
            coluna_nome, operador, token = comando["condicao"]
            if coluna_nome is not None:
                coluna = buscar_coluna(tabela, coluna_nome)
                token = self._preparar_token(coluna, token)
                # As funções existentes são reutilizadas mesmo em tabela vazia.
                validar_operador(coluna, operador)
                validar_token(coluna, token)
                comando["condicao"] = (coluna_nome, operador, token)

        if nome == "INSERIREM":
            if len(comando["valores"]) != len(tabela.colunas) - 1:
                raise ErroIFFARQL("Quantidade de valores inválida.")
            valores = []
            for coluna, token in zip(tabela.colunas[1:], comando["valores"]):
                token = self._preparar_token(coluna, token)
                validar_token(coluna, token)
                valores.append(token)
            comando["valores"] = valores

        if nome == "ATUALIZATABELA":
            for atualizacao in comando["atualizacoes"]:
                coluna = buscar_coluna(tabela, atualizacao["coluna"])
                token = self._preparar_token(coluna, atualizacao["token"])
                if atualizacao["operador"] is None:
                    validar_token(coluna, token)
                atualizacao["token"] = token

    def _alterar_banco(self, banco, comando):
        nome = comando["comando"]
        tabela = comando["tabela"]
        if nome == "CRIATABELA":
            criar_tabela(banco, tabela, comando["colunas"])
            return f"Tabela '{tabela}' criada."
        if nome == "APAGATABELA":
            apagar_tabela(banco, tabela)
            return f"Tabela '{tabela}' apagada."
        if nome == "INSERIREM":
            registro = inserir_em(banco, tabela, comando["valores"])
            return f"Registro inserido com id {registro.id}."
        if nome == "APAGADADOSDE":
            quantidade = apagar_dados(banco, tabela, *comando["condicao"])
            return f"{quantidade} registro(s) removido(s)."
        if nome == "ATUALIZATABELA":
            atualizacoes = comando["atualizacoes"]
            condicao = comando["condicao"]
            if len(atualizacoes) > 1:
                quantidade = atualizar_multiplos(banco, tabela, atualizacoes, *condicao)
            else:
                atualizacao = atualizacoes[0]
                if atualizacao["operador"] is None:
                    quantidade = atualizar_dados(
                        banco, tabela, atualizacao["coluna"], atualizacao["token"], *condicao,
                    )
                else:
                    quantidade = atualizar_com_operacao(
                        banco, tabela, atualizacao["coluna"], atualizacao["operador"],
                        atualizacao["token"], *condicao,
                    )
            return f"{quantidade} registro(s) atualizado(s)."
        raise ErroIFFARQL(f"Comando não implementado: '{nome}'.")

    def _resolver_caminho(self, texto):
        caminho = Path(texto)
        if not caminho.is_absolute() and self._arquivos_em_execucao:
            caminho = self._arquivos_em_execucao[-1].parent / caminho
        return caminho.resolve()

    def _carregar_comandos(self, caminho):
        if caminho.suffix.lower() != ".txt":
            raise ErroIFFARQL("CARREGARIFFARQL exige um arquivo .txt.")
        if caminho in self._arquivos_em_execucao:
            raise ErroIFFARQL("CARREGARIFFARQL não pode carregar um arquivo já em execução.")
        if len(self._arquivos_em_execucao) >= 20:
            raise ErroIFFARQL("Limite de 20 arquivos IFFARQL aninhados atingido.")
        try:
            linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as erro:
            raise ErroIFFARQL(f"Não foi possível ler '{caminho}': {erro}") from erro

        erros = []
        executados = 0
        self._arquivos_em_execucao.append(caminho)
        try:
            for numero, linha in enumerate(linhas, 1):
                if not linha.strip():
                    continue
                try:
                    resultado = self.executar_comando(linha)
                    if resultado.erros:
                        erros.extend(f"{caminho}: linha {numero}: {erro}" for erro in resultado.erros)
                    else:
                        executados += 1
                except ErroIFFARQL as erro:
                    erros.append(f"{caminho}: linha {numero}: {erro}")
        finally:
            self._arquivos_em_execucao.pop()
        return ResultadoComando(f"Arquivo processado: {executados} linha(s) sem erros.", erros)


def executar_comando(interpretador, texto):
    """Ponto de entrada para quem integra uma sessão existente ao programa."""
    return interpretador.executar_comando(texto)
