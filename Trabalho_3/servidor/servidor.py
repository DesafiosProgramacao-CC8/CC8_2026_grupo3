
import socket
import threading
import sys
from pathlib import Path

# Permito iniciar pelo arquivo ou pelo comando python -m
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from Trabalho_3.iffarql.erros import ErroIFFARQL
from Trabalho_3.servidor.protocolo import processar_comando, criar_mensagem_erro
from Trabalho_3.servidor.conexoes import GerenciadorConexoes
from Trabalho_3.servidor.servico_chat import ServicoChat
from Trabalho_3.servidor.banco_chat import ARQUIVO_BANCO


HOST = "0.0.0.0"
PORTA = 42000

TAMANHO_MAXIMO = 4096

gerenciador = GerenciadorConexoes()


def enviar_resposta(id_conexao, resposta):
    gerenciador.enviar_resposta(id_conexao, resposta)


def atender_cliente(conexao, endereco, servico):
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

                        enviar_resposta(id_conexao, resposta)
                        break

                    try:
                        mensagem = dados.decode("utf-8")
                    except UnicodeDecodeError:
                        resposta = criar_mensagem_erro(
                            "ERROCONEXAO",
                            "Codificacao invalida"
                        )

                        enviar_resposta(id_conexao, resposta)
                        break

                    # Não mostro senhas codificadas nem conversas no terminal
                    print(f"Requisição recebida do cliente {id_conexao}")

                    resposta, desconectar = processar_comando(
                        mensagem, servico, id_conexao
                    )

                    if resposta is not None:
                        enviar_resposta(id_conexao, resposta)

                        print(
                            f"Resposta enviada ao cliente "
                            f"{id_conexao}"
                        )

                    if desconectar:
                        break

                    gerenciador.habilitar_avisos(id_conexao)
                    try:
                        servico.entregar_avisos()
                    except ErroIFFARQL:
                        print("Não foi possível confirmar a entrega dos avisos")

    except (ConnectionError, OSError) as erro:
        print(
            f"Erro na conexao {id_conexao}: {erro}"
        )

    finally:
        servico.finalizar_conexao(id_conexao)

        print(f"Cliente {id_conexao} desconectado.")
        print(
            f"Conexoes ativas: "
            f"{gerenciador.quantidade_conexoes()}"
        )


def iniciar_servidor(caminho_banco=ARQUIVO_BANCO):
    servico = ServicoChat(gerenciador, caminho_banco)
    threads = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
            servidor.bind((HOST, PORTA))
            servidor.listen()
            print(f"Servidor iniciado na porta {PORTA}")

            while True:
                conexao, endereco = servidor.accept()
                thread = threading.Thread(
                    target=atender_cliente,
                    args=(conexao, endereco, servico),
                    daemon=True,
                )
                thread.start()
                threads = [ativa for ativa in threads if ativa.is_alive()]
                threads.append(thread)
    finally:
        # Fecho os clientes antes de encerrar a fila do banco
        gerenciador.encerrar_conexoes()
        for thread in threads:
            thread.join()
        servico.fechar()


if __name__ == "__main__":
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    except (ErroIFFARQL, OSError) as erro:
        print(f"Não foi possível iniciar o servidor: {erro}")
