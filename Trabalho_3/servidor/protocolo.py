
TERMINADOR = "#\n"

CONECTAR = 2
CONECTADO = 3
PING = 4
PONG = 5
DESCONECTAR = 32
DESCONECTADO = 33
ERRO = 32768


def criar_mensagem_erro(categoria, descricao):
    return f"{ERRO}|{categoria}|{descricao}|{TERMINADOR}"


def interpretar_mensagem(mensagem):
    # Toda mensagem deve terminar em # seguido de \n.
    if not mensagem.endswith(TERMINADOR):
        return None

    conteudo = mensagem[:-len(TERMINADOR)]

    # O último parâmetro deve terminar com |.
    if not conteudo.endswith("|"):
        return None

    # Os símbolos reservados não podem estar no conteúdo.
    if "#" in conteudo or "\n" in conteudo:
        return None

    partes = conteudo.split("|")

    codigo = partes[0]
    parametros = partes[1:-1]

    if not codigo.isdigit():
        return None

    return int(codigo), parametros


def processar_comando(mensagem):
    resultado = interpretar_mensagem(mensagem)

    if resultado is None:
        return criar_mensagem_erro(
            "ERROCONEXAO",
            "Formato de mensagem invalido"
        ), False

    codigo, parametros = resultado

    # CONECTAR
    if codigo == CONECTAR:
        if parametros == []:
            return f"{CONECTADO}|{TERMINADOR}", False

        return criar_mensagem_erro(
            "ERROCONEXAO",
            "Parametros invalidos para CONECTAR"
        ), False

    # PING
    if codigo == PING:
        if parametros == []:
            return f"{PONG}|{TERMINADOR}", False

        return criar_mensagem_erro(
            "ERROCONEXAO",
            "Parametros invalidos para PING"
        ), False

    # DESCONECTAR
    if codigo == DESCONECTAR:
        if (
            len(parametros) == 1
            and parametros[0].isdigit()
            and int(parametros[0]) > 0
        ):
            return f"{DESCONECTADO}|{TERMINADOR}", True

        return criar_mensagem_erro(
            "ERROCONEXAO",
            "ID invalido para DESCONECTAR"
        ), False

    # Comandos que ainda nao foram implementados.
    return criar_mensagem_erro(
        "ERROCONEXAO",
        "Comando desconhecido ou nao implementado"
    ), False
