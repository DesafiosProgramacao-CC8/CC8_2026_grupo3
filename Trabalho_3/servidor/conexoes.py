
import threading
import socket


class GerenciadorConexoes:

    def __init__(self):
        self.conexoes = {}
        self.lock = threading.Lock()
        self.proximo_id = 1

    def adicionar_conexao(self, conexao, endereco):
        with self.lock:
            id_conexao = self.proximo_id
            self.proximo_id += 1

            self.conexoes[id_conexao] = {
                "socket": conexao,
                "endereco": endereco,
                "id_usuario": None,
                "trava_envio": threading.Lock(),
                "receber_avisos": False,
            }

            return id_conexao

    def remover_conexao(self, id_conexao):
        with self.lock:
            return self.conexoes.pop(id_conexao, None)

    def autenticar_conexao(self, id_conexao, id_usuario):
        with self.lock:
            if id_conexao not in self.conexoes:
                return False

            if (
                type(id_usuario) is not int
                or id_usuario <= 0
            ):
                return False

            # Impede trocar de usuário sem encerrar a sessão.
            if self.conexoes[id_conexao]["id_usuario"] is not None:
                return False

            # Impede o mesmo usuário em duas conexões.
            for dados in self.conexoes.values():
                if dados["id_usuario"] == id_usuario:
                    return False

            self.conexoes[id_conexao]["id_usuario"] = id_usuario
            return True

    def obter_usuario(self, id_conexao):
        with self.lock:
            dados = self.conexoes.get(id_conexao)

            if dados is None:
                return None

            return dados["id_usuario"]

    def usuario_esta_online(self, id_usuario):
        with self.lock:
            return any(
                dados["id_usuario"] == id_usuario
                for dados in self.conexoes.values()
            )

    def listar_usuarios_online(self):
        with self.lock:
            return [
                dados["id_usuario"]
                for dados in self.conexoes.values()
                if dados["id_usuario"] is not None
            ]

    def listar_conexoes(self):
        with self.lock:
            return [
                {
                    "id": id_conexao,
                    "endereco": dados["endereco"],
                    "id_usuario": dados["id_usuario"]
                }
                for id_conexao, dados in self.conexoes.items()
            ]

    def quantidade_conexoes(self):
        with self.lock:
            return len(self.conexoes)

    def enviar_resposta(self, id_conexao, mensagem):
        with self.lock:
            dados = self.conexoes.get(id_conexao)
        if dados is None:
            raise ConnectionError("Conexão não encontrada")
        # Uma resposta e um aviso não podem misturar bytes no mesmo socket
        with dados["trava_envio"]:
            dados["socket"].sendall(mensagem.encode("utf-8"))

    def habilitar_avisos(self, id_conexao):
        with self.lock:
            dados = self.conexoes.get(id_conexao)
            if dados is not None and dados["id_usuario"] is not None:
                # Primeiro o cliente recebe a confirmação de login
                dados["receber_avisos"] = True

    def enviar_para_usuario(self, id_usuario, mensagem):
        with self.lock:
            destino = None
            for id_conexao, dados in self.conexoes.items():
                if dados["id_usuario"] == id_usuario and dados["receber_avisos"]:
                    destino = id_conexao
                    break
        if destino is None:
            return False
        try:
            self.enviar_resposta(destino, mensagem)
            return True
        except OSError:
            return False

    def encerrar_conexoes(self):
        with self.lock:
            conexoes = [dados["socket"] for dados in self.conexoes.values()]
        for conexao in conexoes:
            try:
                conexao.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
