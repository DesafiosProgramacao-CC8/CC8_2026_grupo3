
TERMINADOR = "#\n"

# Codigos enviados pelo cliente.
COMANDOS_CLIENTE = {
    2: "CONECTAR",
    4: "PING",
    8: "REGISTRAR",
    16: "AUTENTICAR",
    32: "DESCONECTAR",
    64: "LISTARUSUARIOS",
    128: "VERIFICARNOTIFICACAO",
    256: "NOVAAMIZADE",
    258: "CONEXAOAMIZADE",
    512: "ALTERARSILENCIAMENTO",
    1024: "PEGARMENSAGENS",
    2048: "ENVIARMENSAGEM",
    4096: "PEGARHISTORICOMENSAGENS",
    8192: "VERPERFIL",
    16384: "ATUALIZARPERFIL"
}

# Quantidade de parametros por comando.
PARAMETROS_COMANDOS = {
    2: 0,
    4: 0,
    8: 4,
    16: 2,
    32: 1,
    64: 2,
    128: 1,
    256: 2,
    258: 3,
    512: 2,
    1024: 2,
    2048: 3,
    4096: 2,
    8192: 1,
    16384: 4
}

# Categorias de erro previstas no protocolo.
CATEGORIAS_ERRO = {
    8: "ERROREGISTRO",
    16: "ERROAUTENTICACAO",
    64: "ERROLISTARUSUARIOS",
    1024: "ERROMENSAGENS",
    2048: "ERROENVIARMENSAGEM",
    4096: "ERROHISTORICOMENSAGENS",
    8192: "ERROVERPERFIL",
    16384: "ERROATUALIZARPERFIL"
}


def criar_mensagem_erro(categoria, descricao):
    return f"32768|{categoria}|{descricao}|{TERMINADOR}"


def interpretar_mensagem(mensagem):
    if not isinstance(mensagem, str):
        return None

    if not mensagem.endswith(TERMINADOR):
        return None

    conteudo = mensagem[:-len(TERMINADOR)]

    if not conteudo.endswith("|"):
        return None

    if "#" in conteudo or "\n" in conteudo:
        return None

    partes = conteudo.split("|")

    codigo = partes[0]
    parametros = partes[1:-1]

    if not codigo.isdigit():
        return None

    return int(codigo), parametros


def id_valido(valor):
    return valor.isdigit() and int(valor) > 0


def validar_parametros(codigo, parametros):
    quantidade = PARAMETROS_COMANDOS.get(codigo)

    if quantidade is None:
        return False

    if len(parametros) != quantidade:
        return False

    # Comandos sem parametros.
    if codigo in (2, 4):
        return True

    # Cadastro.
    if codigo == 8:
        nome, apelido, nascimento, senha_hash = parametros

        return all((
            bool(nome.strip()),
            bool(apelido.strip()),
            bool(nascimento.strip()),
            bool(senha_hash.strip())
        ))

    # Autenticacao.
    if codigo == 16:
        apelido, senha_hash = parametros

        return bool(apelido.strip()) and bool(senha_hash.strip())

    # Comandos que recebem somente um ID.
    if codigo in (32, 128, 8192):
        return id_valido(parametros[0])

    # Listar usuarios: 0 = ONLINE, 1 = AMIGOS.
    if codigo == 64:
        return (
            id_valido(parametros[0])
            and parametros[1] in ("0", "1")
        )

    # Operacoes com dois IDs.
    if codigo in (256, 512, 4096):
        return all(id_valido(p) for p in parametros)

    # Responder solicitacao de amizade.
    if codigo == 258:
        return (
            id_valido(parametros[0])
            and id_valido(parametros[1])
            and parametros[2] in ("VERDADEIRO", "FALSO")
        )

    # Consultar mensagens: segundo ID opcional.
    if codigo == 1024:
        return (
            id_valido(parametros[0])
            and (
                parametros[1] == ""
                or id_valido(parametros[1])
            )
        )

    # Enviar mensagem geral ou privada.
    if codigo == 2048:
        remetente, destinatario, texto = parametros

        return (
            id_valido(remetente)
            and (destinatario == "" or id_valido(destinatario))
            and bool(texto.strip())
        )

    # Atualizar perfil.
    if codigo == 16384:
        id_usuario, nome, nascimento, senha_hash = parametros

        return (
            id_valido(id_usuario)
            and bool(nome.strip())
            and bool(nascimento.strip())
            and bool(senha_hash.strip())
        )

    return False


def processar_comando(mensagem):
    resultado = interpretar_mensagem(mensagem)

    if resultado is None:
        return criar_mensagem_erro(
            "ERROCONEXAO",
            "Formato de mensagem invalido"
        ), False

    codigo, parametros = resultado

    if codigo not in COMANDOS_CLIENTE:
        return criar_mensagem_erro(
            "ERROCONEXAO",
            "Comando desconhecido ou nao implementado"
        ), False

    categoria = CATEGORIAS_ERRO.get(
        codigo, "ERROCONEXAO"
    )

    if not validar_parametros(codigo, parametros):
        if codigo == 32:
            descricao = "ID invalido para DESCONECTAR"
        elif codigo == 2:
            descricao = "Parametros invalidos para CONECTAR"
        elif codigo == 4:
            descricao = "Parametros invalidos para PING"
        else:
            descricao = "Parametros invalidos"

        return criar_mensagem_erro(
            categoria, descricao
        ), False

    # Comandos basicos ja implementados.
    if codigo == 2:
        return "3|#\n", False

    if codigo == 4:
        return "5|#\n", False

    if codigo == 32:
        return "33|#\n", True

    # Os demais comandos aguardam suas regras de negocio.
    return criar_mensagem_erro(
        categoria,
        "Operacao ainda nao integrada"
    ), False
