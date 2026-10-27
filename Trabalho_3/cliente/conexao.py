#Transporte TCP do cliente, sem regras de negócio nem dependência do IFFARQL.

import socket
import threading

TERMINADOR = "#\n"
LIMITE_BYTES = 4096


class ErroConexao(Exception):
    """Falha de comunicação ou resposta inválida."""

class ConexaoTCP:
    def __init__(self):
        self._socket = None
        self._arquivo = None
        self._lock = threading.Lock()

    @property
    def conectado(self):
        return self._socket is not None

    def conectar(self, host="127.0.0.1", porta=42000, timeout=4):
        with self._lock:
            self._fechar()
            try:
                self._socket = socket.create_connection((host, porta), timeout=timeout)
                self._socket.settimeout(timeout)
                self._arquivo = self._socket.makefile("rb")
                resposta = self._trocar("2|#\n")
                if resposta != "3|#\n":
                    raise ErroConexao(f"Resposta inesperada: {resposta.strip()}")
            except (OSError, ErroConexao) as erro:
                self._fechar()
                raise ErroConexao(str(erro)) from erro

    def ping(self):
        with self._lock:
            resposta = self._trocar("4|#\n")
            if resposta != "5|#\n":
                raise ErroConexao(f"Resposta inesperada: {resposta.strip()}")
            return True

    def _trocar(self, mensagem):
        if not self.conectado:
            raise ErroConexao("Não há conexão ativa")
        try:
            self._socket.sendall(mensagem.encode("utf-8"))
            dados = self._arquivo.readline(LIMITE_BYTES + 1)
            if not dados or len(dados) > LIMITE_BYTES:
                raise ErroConexao("Conexão encerrada ou resposta muito longa")
            resposta = dados.decode("utf-8")
            if not resposta.endswith(TERMINADOR):
                raise ErroConexao("Resposta sem terminador do protocolo")
            return resposta
        except (OSError, UnicodeError) as erro:
            self._fechar()
            raise ErroConexao(str(erro)) from erro

    def desconectar(self):
        # O comando 32 exige ID autenticado. Antes do login, fecha-se o socket.
        with self._lock:
            self._fechar()

    def _fechar(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        if self._arquivo:
            try:
                self._arquivo.close()
            except OSError:
                pass
        if self._socket:
            self._socket.close()
        self._arquivo = None
        self._socket = None
