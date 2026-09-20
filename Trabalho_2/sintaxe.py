import re

from erros import ErroIFFARQL
from tokenizador import ASPAS, converter_valor, tokenizar


COMANDOS_ARQUIVO = ("SALVARBD", "CARREGARBD", "CARREGARIFFARQL")
COMPARADORES = ("<", "<=", ">", ">=", "==", "<>")
OPERACOES = ("+", "-", "*", "/")


class AnalisadorComando:
    """Lê as partes de um comando em ordem, sem modificar o banco."""

    def __init__(self, partes):
        self.partes = partes
        self.posicao = 0

    def atual(self):
        if self.posicao < len(self.partes):
            return self.partes[self.posicao]
        return None

    def ler(self):
        parte = self.atual()
        if parte is None:
            raise ErroIFFARQL("Comando incompleto.")
        self.posicao += 1
        return parte

    def exigir(self, esperado):
        recebido = self.ler()
        if recebido != esperado:
            raise ErroIFFARQL(f"Era esperado '{esperado}', mas foi recebido '{recebido}'.")

    def ler_nome(self):
        nome = self.ler()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
            raise ErroIFFARQL(f"Nome inválido: '{nome}'. Use letras, números e sublinhado.")
        return nome

    def ler_valor(self):
        texto = self.ler()
        # O tokenizador separa sinais para também reconhecer idade=idade-3.
        if texto in ("+", "-"):
            texto += self.ler()
        return converter_valor(texto)

    def ler_condicao(self):
        if self.atual() is None:
            return (None, None, None)
        self.exigir("ONDE")
        coluna = self.ler_nome()
        operador = self.ler()
        if operador not in COMPARADORES:
            raise ErroIFFARQL(f"Comparador inválido: '{operador}'.")
        return (coluna, operador, self.ler_valor())

    def ler_colunas(self):
        self.exigir("(")
        colunas = []
        while self.atual() != ")":
            coluna = {"nome": self.ler_nome(), "tipo": self.ler_nome()}
            if self.atual() == "CHAVESTRANGEIRA":
                self.ler()
                coluna["chave_estrangeira"] = self.ler_nome()
            colunas.append(coluna)
        self.exigir(")")
        return colunas

    def ler_valores(self):
        self.exigir("VALOR")
        self.exigir("(")
        valores = []
        while self.atual() != ")":
            valores.append(self.ler_valor())
        self.exigir(")")
        return valores

    def ler_atualizacoes(self):
        atualizacoes = []
        while self.atual() == "COM":
            self.ler()
            coluna = self.ler_nome()
            self.exigir("=")
            operador = None
            tem_operacao = (
                self.posicao + 1 < len(self.partes)
                and self.partes[self.posicao + 1] in OPERACOES
            )
            if self.atual() == coluna and tem_operacao:
                self.ler()
                operador = self.ler()
                if operador not in OPERACOES:
                    raise ErroIFFARQL(f"Operação inválida: '{operador}'.")
            token = self.ler_valor()
            atualizacoes.append({"coluna": coluna, "operador": operador, "token": token})
        if not atualizacoes:
            raise ErroIFFARQL("ATUALIZATABELA exige pelo menos um COM.")
        return atualizacoes

    def finalizar(self):
        if self.atual() is not None:
            raise ErroIFFARQL(f"Trecho inesperado no fim do comando: '{self.atual()}'.")


def analisar_comando(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ErroIFFARQL("Comando vazio ou inválido.")

    inicio = texto.strip().split(maxsplit=1)
    comando = inicio[0]
    if comando in COMANDOS_ARQUIVO:
        # Caminhos podem conter / ou -, que têm outro significado em expressões.
        if len(inicio) != 2:
            raise ErroIFFARQL(f"{comando} exige o nome de um arquivo.")
        caminho = inicio[1].strip()
        if caminho[0] in ASPAS:
            caminho = converter_valor(caminho).valor
        elif any(caractere.isspace() for caractere in caminho) or any(
            aspas in caminho for aspas in '"“”'
        ):
            raise ErroIFFARQL("Use aspas ao redor de caminhos com espaços.")
        if not caminho or "\x00" in caminho:
            raise ErroIFFARQL("Nome de arquivo vazio ou inválido.")
        return {"comando": comando, "caminho": caminho}

    analisador = AnalisadorComando(tokenizar(texto))
    comando = analisador.ler()
    comandos_tabela = (
        "CRIATABELA", "APAGATABELA", "INSERIREM", "MOSTRADADOSDE",
        "APAGADADOSDE", "ATUALIZATABELA",
    )
    if comando not in comandos_tabela:
        raise ErroIFFARQL(f"Comando desconhecido: '{comando}'. Use comandos em caixa alta.")

    resultado = {"comando": comando, "tabela": analisador.ler_nome()}
    if comando == "CRIATABELA":
        resultado["colunas"] = analisador.ler_colunas()
    elif comando == "INSERIREM":
        resultado["valores"] = analisador.ler_valores()
    elif comando == "ATUALIZATABELA":
        resultado["atualizacoes"] = analisador.ler_atualizacoes()

    if comando in ("MOSTRADADOSDE", "APAGADADOSDE", "ATUALIZATABELA"):
        resultado["condicao"] = analisador.ler_condicao()
    analisador.finalizar()
    return resultado
