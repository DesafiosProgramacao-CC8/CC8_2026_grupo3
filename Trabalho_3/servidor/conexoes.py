
import threading


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
                "id_usuario": None
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
