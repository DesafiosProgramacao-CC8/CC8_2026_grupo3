
import socket
import threading

try:
    from .protocolo import (
        processar_comando,
        criar_mensagem_erro
    )
    from .conexoes import GerenciadorConexoes
except ImportError:
    from protocolo import (
        processar_comando,
        criar_mensagem_erro
    )
    from conexoes import GerenciadorConexoes


HOST = "0.0.0.0"
PORTA = 42000

TAMANHO_MAXIMO = 4096

gerenciador = GerenciadorConexoes()


def enviar_resposta(conexao, resposta):
    conexao.sendall(resposta.encode("utf-8"))


def atender_cliente(conexao, endereco):
    id_conexao = gerenciador.adicionar_conexao(
        conexao, endereco
    )

    print(f"Cliente {id_conexao} conectado: {endereco}")
    print(
        f"Conexoes ativas: "
        f"{gerenciador.quantidade_conexoes()}"
    )

    try:
        with conexao:
            with conexao.makefile("rb") as arquivo:

                while True:
                    # Limita o tamanho de cada mensagem.
                    dados = arquivo.readline(TAMANHO_MAXIMO + 1)

                    if not dados:
                        break

                    if len(dados) > TAMANHO_MAXIMO:
                        resposta = criar_mensagem_erro(
                            "ERROCONEXAO",
                            "Mensagem muito grande"
                        )

                        enviar_resposta(conexao, resposta)
                        break

                    try:
                        mensagem = dados.decode("utf-8")
                    except UnicodeDecodeError:
                        resposta = criar_mensagem_erro(
                            "ERROCONEXAO",
                            "Codificacao invalida"
                        )

                        enviar_resposta(conexao, resposta)
                        break

                    print(
                        f"Cliente {id_conexao} enviou: "
                        f"{mensagem!r}"
                    )

                    resposta, desconectar = processar_comando(
                        mensagem
                    )

                    if resposta is not None:
                        enviar_resposta(conexao, resposta)

                        print(
                            f"Resposta enviada ao cliente "
                            f"{id_conexao}: {resposta!r}"
                        )

                    if desconectar:
                        break

    except (ConnectionError, OSError) as erro:
        print(
            f"Erro na conexao {id_conexao}: {erro}"
        )

    finally:
        gerenciador.remover_conexao(id_conexao)

        print(f"Cliente {id_conexao} desconectado.")
        print(
            f"Conexoes ativas: "
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
