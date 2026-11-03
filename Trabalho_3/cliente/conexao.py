#Transporte TCP do cliente, sem regras de negócio nem dependência do IFFARQL.

import socket
import threading

TERMINADOR = "#\n"
LIMITE_BYTES = 4096
from protocolo_cliente import criar_mensagem, interpretar_resposta, ErroProtocolo


class ErroConexao(Exception):
    """Falha de comunicação ou resposta inválida."""

class ConexaoTCP:
    def __init__(self):
        self._socket = None
        self._arquivo = None
        self._lock = threading.Lock()
        self.id_usuario = None
        self.avisos = []

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

    def requisitar(self, codigo, *parametros):
        #Envia comandos reais e interpreta a resposta.
        with self._lock:
            try:
                self._socket.sendall(criar_mensagem(codigo, *parametros).encode("utf-8"))
                while True:
                    resposta = self._ler()
                    numero, campos = interpretar_resposta(resposta)
                    if numero in (257, 259):
                        self.avisos.append((numero, campos))
                        continue
                    if numero == 32768:
                        raise ErroConexao(campos[1] or campos[0])
                    return numero, campos
            except (OSError, ErroProtocolo, AttributeError, UnicodeError) as erro:
                self._fechar()
                raise ErroConexao(str(erro)) from erro

    def enviar_sem_resposta(self, codigo, *parametros):
        #Os comandos de amizade não possuem resposta imediata.
        with self._lock:
            if not self.conectado:
                raise ErroConexao("Não há conexão ativa")
            try:
                #O PING marca o fim da resposta, que pode ser um erro.
                self._socket.sendall((criar_mensagem(codigo, *parametros) + "4|#\n").encode("utf-8"))
                erro_servidor = None
                while True:
                    numero, campos = interpretar_resposta(self._ler())
                    if numero in (257, 259):
                        self.avisos.append((numero, campos))
                    elif numero == 32768:
                        erro_servidor = campos[1] or campos[0]
                    elif numero == 5:
                        break
                    else:
                        raise ErroProtocolo("Resposta inesperada do servidor.")
            except (OSError, ErroProtocolo, UnicodeError) as erro:
                self._fechar()
                raise ErroConexao(str(erro)) from erro
            if erro_servidor:
                raise ErroConexao(erro_servidor)

    def retirar_avisos(self):
        #Retira os avisos recebidos durante as requisições.
        with self._lock:
            avisos = self.avisos[:]
            self.avisos.clear()
            return avisos

    def _ler(self):
        dados = self._arquivo.readline(LIMITE_BYTES + 1)
        if not dados or len(dados) > LIMITE_BYTES:
            self._fechar()
            raise ErroConexao("Conexão encerrada ou resposta muito longa")
        resposta = dados.decode("utf-8")
        if not resposta.endswith(TERMINADOR):
            raise ErroConexao("Resposta sem terminador")
        return resposta

    def ping(self):
        with self._lock:
            resposta = self._trocar("4|#\n")
            #Guarda avisos de amizade que chegaram antes do PONG.
            while resposta.startswith(("257|", "259|")):
                try:
                    self.avisos.append(interpretar_resposta(resposta))
                    resposta = self._ler()
                except (OSError, ErroProtocolo, UnicodeError) as erro:
                    self._fechar()
                    raise ErroConexao(str(erro)) from erro
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
        #Encerra a sessão autenticada antes de fechar o socket.
        if self.conectado and self.id_usuario:
            try:
                self.requisitar(32, self.id_usuario)
            except ErroConexao:
                pass
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
        self.id_usuario = None
