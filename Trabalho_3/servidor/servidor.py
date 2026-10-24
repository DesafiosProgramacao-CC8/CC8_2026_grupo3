
import socket
import threading

try:
    from .protocolo import processar_comando
except ImportError:
    from protocolo import processar_comando


HOST = "0.0.0.0"
PORTA = 42000


def atender_cliente(conexao, endereco):
    print(f"Cliente conectado: {endereco}")

    try:
        with conexao:
            with conexao.makefile("rb") as arquivo:

                while True:
                    dados = arquivo.readline()

                    if not dados:
                        break

                    mensagem = dados.decode("utf-8")

                    print(f"Recebido de {endereco}: {mensagem!r}")

                    resposta, desconectar = processar_comando(mensagem)

                    if resposta is not None:
                        conexao.sendall(resposta.encode("utf-8"))
                        print(f"Resposta enviada: {resposta!r}")

                    else:
                        print("Comando inválido ou não implementado.")

                    if desconectar:
                        break

    except (ConnectionError, OSError, UnicodeDecodeError) as erro:
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
