
import socket
import threading

try:
    from .protocolo import processar_comando
    from .conexoes import GerenciadorConexoes
except ImportError:
    from protocolo import processar_comando
    from conexoes import GerenciadorConexoes


HOST = "0.0.0.0"
PORTA = 42000

gerenciador = GerenciadorConexoes()


def atender_cliente(conexao, endereco):
    id_conexao = gerenciador.adicionar_conexao(
        conexao, endereco
    )

    print(f"Cliente {id_conexao} conectado: {endereco}")
    print(
        f"Conexões ativas: "
        f"{gerenciador.quantidade_conexoes()}"
    )

    try:
        with conexao:
            with conexao.makefile("rb") as arquivo:

                while True:
                    dados = arquivo.readline()

                    if not dados:
                        break

                    mensagem = dados.decode("utf-8")

                    print(
                        f"Cliente {id_conexao} enviou: "
                        f"{mensagem!r}"
                    )

                    resposta, desconectar = processar_comando(
                        mensagem
                    )

                    if resposta is not None:
                        conexao.sendall(
                            resposta.encode("utf-8")
                        )

                    else:
                        print(
                            f"Comando inválido ou não implementado "
                            f"do cliente {id_conexao}."
                        )

                    if desconectar:
                        break

    except (ConnectionError, OSError, UnicodeDecodeError) as erro:
        print(
            f"Erro na conexão {id_conexao}: {erro}"
        )

    finally:
        gerenciador.remover_conexao(id_conexao)

        print(f"Cliente {id_conexao} desconectado.")
        print(
            f"Conexões ativas: "
            f"{gerenciador.quantidade_conexoes()}"
        )


def iniciar_servidor():
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as servidor:

        servidor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        servidor.bind((HOST, PORTA))
        servidor.listen()

        print(f"Servidor iniciado na porta {PORTA}")

        while True:
            conexao, endereco = servidor.accept()

            thread = threading.Thread(
                target=atender_cliente,
                args=(conexao, endereco),
                daemon=True
            )

            thread.start()


if __name__ == "__main__":
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
