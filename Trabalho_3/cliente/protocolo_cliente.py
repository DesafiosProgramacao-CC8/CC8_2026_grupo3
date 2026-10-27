#Construção e interpretação de mensagens do protocolo IFFARCHAT.

TERMINADOR = "#\n"
PARAMETROS_CLIENTE = {
    2: 0, 4: 0, 8: 4, 16: 2, 32: 1, 64: 2, 128: 1,
    256: 2, 258: 3, 512: 2, 1024: 2, 2048: 3,
    4096: 2, 8192: 1, 16384: 4,
}

# Quantidades fixas de parâmetros; respostas de listas usam validação específica.
PARAMETROS_SERVIDOR = {
    3: 0, 5: 0, 9: 0, 17: 1, 33: 0, 257: 1,
    259: 2, 513: 0, 2049: 0, 8193: 4, 16385: 0, 32768: 2,
}
RESPPOSTAS_VARIAVEIS = {65: 2, 129: 1, 1025: 5, 4097: 5}

class ErroProtocolo(ValueError):
    """Mensagem incompatível com o protocolo IFFARCHAT."""

def _validar_campo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (str, int)):
        raise ErroProtocolo("Parâmetros devem ser texto ou número inteiro.")
    campo = str(valor)
    if "|" in campo or "#" in campo or "\n" in campo or "\r" in campo:
        raise ErroProtocolo("Parâmetro contém caractere reservado.")
    return campo

def criar_mensagem(codigo, *parametros):
    """Cria comando do cliente terminado em '#\\n'."""
    if isinstance(codigo, bool) or not isinstance(codigo, int) or codigo not in PARAMETROS_CLIENTE:
        raise ErroProtocolo("Código de comando desconhecido.")
    if len(parametros) != PARAMETROS_CLIENTE[codigo]:
        raise ErroProtocolo("Quantidade de parâmetros inválida.")
    campos = [_validar_campo(p) for p in parametros]
    def id_valido(s):
        return s.isascii() and s.isdecimal() and int(s) > 0
    if codigo in (32, 128, 8192) and not id_valido(campos[0]):
        raise ErroProtocolo("ID inválido.")
    if codigo in (256, 512, 4096) and not all(map(id_valido, campos)):
        raise ErroProtocolo("IDs inválidos.")
    if codigo == 64 and (not id_valido(campos[0]) or campos[1] not in ('0', '1')):
        raise ErroProtocolo("Lista de usuários inválida.")
    if codigo == 258 and (not all(map(id_valido, campos[:2])) or campos[2] not in ('VERDADEIRO', 'FALSO')):
        raise ErroProtocolo("Resposta de amizade inválida.")
    if codigo in (1024, 2048) and (not id_valido(campos[0]) or (campos[1] and not id_valido(campos[1]))):
        raise ErroProtocolo("ID inválido.")
    if codigo == 2048 and not campos[2].strip():
        raise ErroProtocolo("Mensagem vazia.")
    if codigo == 16384 and (not id_valido(campos[0]) or not all(s.strip() for s in campos[1:])):
        raise ErroProtocolo("Dados de perfil inválidos.")
    if codigo in (8, 16) and not all(s.strip() for s in campos):
        raise ErroProtocolo("Campos obrigatórios não preenchidos.")
    return f"{codigo}|" + "|".join(campos) + ("|" if campos else "") + TERMINADOR

def interpretar_resposta(mensagem):
    """Retorna (código, lista de parâmetros), preservando campos vazios."""
    if not isinstance(mensagem, str) or not mensagem.endswith(TERMINADOR):
        raise ErroProtocolo("Terminador ausente ou mensagem inválida.")
    corpo = mensagem[:-len(TERMINADOR)]
    if not corpo.endswith('|') or '#' in corpo or '\n' in corpo or '\r' in corpo:
        raise ErroProtocolo("Formato inválido.")
    partes = corpo.split('|')
    if not partes[0].isascii() or not partes[0].isdecimal():
        raise ErroProtocolo("Código inválido.")
    codigo = int(partes[0])
    campos = partes[1:-1]
    if codigo in PARAMETROS_SERVIDOR:
        if len(campos) != PARAMETROS_SERVIDOR[codigo]:
            raise ErroProtocolo("Quantidade de parâmetros da resposta inválida.")
    elif codigo in RESPPOSTAS_VARIAVEIS:
        if len(campos) % RESPPOSTAS_VARIAVEIS[codigo] != 0:
            raise ErroProtocolo("Lista de parâmetros incompleta.")
    else:
        raise ErroProtocolo("Código de resposta desconhecido.")
    return codigo, campos
