
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
                "endereco": endereco
            }

            return id_conexao

    def remover_conexao(self, id_conexao):
        with self.lock:
            return self.conexoes.pop(id_conexao, None)

    def listar_conexoes(self):
        with self.lock:
            return [
                {
                    "id": id_conexao,
                    "endereco": dados["endereco"]
                }
                for id_conexao, dados in self.conexoes.items()
            ]

    def quantidade_conexoes(self):
        with self.lock:
            return len(self.conexoes)
