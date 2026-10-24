
import socket
import threading

HOST = "0.0.0.0"
PORTA = 42000


def atender_cliente(conexao, endereco):
    print(f"Cliente conectado: {endereco}")

    try:
        with conexao:
            arquivo = conexao.makefile("rb")

            try:
                while True:
                    dados = arquivo.readline()

                    if not dados:
                        break

                    mensagem = dados.decode("utf-8")

                    print(f"Recebido de {endereco}: {mensagem!r}")

                    # CONECTAR
                    if mensagem == "2|#\n":
                        conexao.sendall(b"3|#\n")
                        print("Resposta CONECTADO enviada.")

                    # PING
                    elif mensagem == "4|#\n":
                        conexao.sendall(b"5|#\n")
                        print("Resposta PONG enviada.")

                    # DESCONECTAR
                    elif mensagem.startswith("32|"):
                        partes = mensagem.split("|")

                        if (
                            len(partes) == 3
                            and partes[0] == "32"
                            and partes[1].isdigit()
                            and partes[2] == "#\n"
                        ):
                            conexao.sendall(b"33|#\n")
                            print("Resposta DESCONECTADO enviada.")
                            break

                        else:
                            print("Comando DESCONECTAR inválido.")

                    else:
                        print("Comando ainda não implementado.")

            finally:
                arquivo.close()

    except (ConnectionError, OSError) as erro:
        print(f"Erro na conexão com {endereco}: {erro}")

    finally:
        print(f"Cliente desconectado: {endereco}")


def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:

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
