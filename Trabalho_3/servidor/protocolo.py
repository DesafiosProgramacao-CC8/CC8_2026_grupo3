
TERMINADOR = "#\n"

CONECTAR = 2
CONECTADO = 3
PING = 4
PONG = 5
DESCONECTAR = 32
DESCONECTADO = 33


def interpretar_mensagem(mensagem):
    if not mensagem.endswith(TERMINADOR):
        return None

    conteudo = mensagem[:-len(TERMINADOR)]

    if not conteudo.endswith("|"):
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
        return None, False

    codigo, parametros = resultado

    if codigo == CONECTAR and parametros == []:
        return "3|#\n", False

    elif codigo == PING and parametros == []:
        return "5|#\n", False

    elif codigo == DESCONECTAR:
        if len(parametros) == 1 and parametros[0].isdigit():
            return "33|#\n", True

    return None, False
