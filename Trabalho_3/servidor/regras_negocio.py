from datetime import date, datetime


class ErroNegocio(Exception):
    pass


def validar_texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ErroNegocio(f"Informe {campo}")
    if any(caractere in valor for caractere in "|#\n\r"):
        raise ErroNegocio(f"O campo {campo} contém um caractere reservado")
    return valor.strip()


def validar_nascimento(nascimento):
    try:
        data = datetime.strptime(nascimento, "%d/%m/%Y").date()
        formato = f"{data.day:02d}/{data.month:02d}/{data.year:04d}"
        if nascimento != formato or data > date.today():
            raise ValueError
        return data
    except (TypeError, ValueError):
        raise ErroNegocio("Informe uma data válida no formato DD/MM/AAAA") from None


class RegrasNegocio:
    def __init__(self, banco):
        self.banco = banco

    def obter_usuario(self, id_usuario):
        if type(id_usuario) is not int or id_usuario <= 0:
            raise ErroNegocio("ID de usuário inválido")
        usuario = self.banco.buscar("Usuario", id_usuario)
        if usuario is None:
            raise ErroNegocio("Usuário não encontrado")
        return usuario

    def cadastrar(self, nome, apelido, nascimento, senha_hash):
        nome = validar_texto(nome, "nome")
        apelido = validar_texto(apelido, "apelido")
        validar_nascimento(nascimento)
        senha_hash = validar_texto(senha_hash, "senha codificada")

        # Comparo sem diferenciar letras maiúsculas e minúsculas
        for usuario in self.banco.listar("Usuario"):
            if usuario["apelido"].casefold() == apelido.casefold():
                raise ErroNegocio("Este apelido já está em uso")

        # A senha já chega codificada pelo cliente
        usuario = self.banco.inserir("Usuario", [nome, apelido, nascimento, senha_hash])
        return usuario["id"]

    def autenticar(self, apelido, senha_hash):
        apelido = validar_texto(apelido, "apelido")
        senha_hash = validar_texto(senha_hash, "senha codificada")
        for usuario in self.banco.listar("Usuario"):
            if usuario["apelido"].casefold() == apelido.casefold():
                if usuario["senha"] == senha_hash:
                    return usuario["id"]
                break
        raise ErroNegocio("Apelido ou senha inválidos")

    def ver_perfil(self, id_usuario):
        usuario = self.obter_usuario(id_usuario)
        nascimento = datetime.strptime(usuario["data_nascimento"], "%d/%m/%Y").date()
        hoje = date.today()
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1

        # O perfil público não mostra a senha nem a data de nascimento
        return {
            "id": usuario["id"], "nome": usuario["nome_completo"],
            "apelido": usuario["apelido"], "idade": idade,
        }

    def atualizar_perfil(self, id_usuario, nome, nascimento, senha_hash):
        usuario = self.obter_usuario(id_usuario)
        if usuario["senha"] != senha_hash:
            raise ErroNegocio("Senha atual inválida")
        nome = validar_texto(nome, "nome")
        validar_nascimento(nascimento)
        self.banco.atualizar("Usuario", id_usuario, {
            "nome_completo": nome, "data_nascimento": nascimento,
        })

    def buscar_amizade(self, id_usuario, id_amigo):
        for amizade in self.banco.listar("Amizade"):
            if (amizade["id_usuario_1"] == id_usuario
                    and amizade["id_usuario_2"] == id_amigo):
                return amizade
        return None

    def exigir_amizade(self, id_usuario, id_amigo):
        self.obter_usuario(id_usuario)
        self.obter_usuario(id_amigo)
        amizade = self.buscar_amizade(id_usuario, id_amigo)
        if amizade is None or amizade["pendente"]:
            raise ErroNegocio("É preciso aceitar a amizade antes de conversar")
        return amizade

    def solicitar_amizade(self, id_usuario, id_amigo):
        self.obter_usuario(id_usuario)
        self.obter_usuario(id_amigo)
        if id_usuario == id_amigo:
            raise ErroNegocio("Não é possível adicionar você mesmo")
        if self.buscar_amizade(id_usuario, id_amigo) is not None:
            raise ErroNegocio("Já existe uma amizade ou um pedido entre vocês")

        # Crio uma linha para cada direção da amizade
        self.banco.inserir("Amizade", [id_usuario, id_amigo, True, False, True, True, 0])
        self.banco.inserir("Amizade", [id_amigo, id_usuario, True, False, True, False, 0])
        self.banco.inserir("AvisoAmizade", [id_amigo, id_usuario, 257, ""])

    def responder_amizade(self, id_usuario, id_amigo, aceitar):
        if type(aceitar) is not bool:
            raise ErroNegocio("Resposta de amizade inválida")
        amizade = self.buscar_amizade(id_usuario, id_amigo)
        if amizade is None or not amizade["pendente"] or amizade["solicitante"]:
            raise ErroNegocio("Não existe um pedido recebido desse usuário")
        inversa = self.buscar_amizade(id_amigo, id_usuario)

        if aceitar:
            for registro in (amizade, inversa):
                self.banco.atualizar("Amizade", registro["id"], {
                    "pendente": False, "bloqueado": False,
                })
        else:
            # A rejeição remove as duas linhas, como pede o enunciado
            self.banco.remover("Amizade", amizade["id"])
            self.banco.remover("Amizade", inversa["id"])

        for aviso in self.banco.listar("AvisoAmizade"):
            if (aviso["codigo"] == 257 and aviso["destinatario"] == id_usuario
                    and aviso["origem"] == id_amigo):
                self.banco.remover("AvisoAmizade", aviso["id"])
        resposta = "VERDADEIRO" if aceitar else "FALSO"
        self.banco.inserir("AvisoAmizade", [id_amigo, id_usuario, 259, resposta])

    def preparar_avisos_login(self, id_usuario):
        avisos = self.banco.listar("AvisoAmizade")
        for amizade in self.banco.listar("Amizade"):
            if (amizade["id_usuario_1"] != id_usuario or not amizade["pendente"]
                    or amizade["solicitante"]):
                continue
            id_amigo = amizade["id_usuario_2"]
            ja_tem_aviso = any(
                aviso["codigo"] == 257 and aviso["destinatario"] == id_usuario
                and aviso["origem"] == id_amigo for aviso in avisos
            )
            if not ja_tem_aviso:
                # O convite reaparece se o cliente fechou antes de responder
                self.banco.inserir("AvisoAmizade", [id_usuario, id_amigo, 257, ""])

    def alterar_silenciamento(self, id_usuario, id_amigo):
        amizade = self.exigir_amizade(id_usuario, id_amigo)
        bloqueado = not amizade["bloqueado"]
        # Só altero a preferência de quem fez o pedido
        self.banco.atualizar("Amizade", amizade["id"], {"bloqueado": bloqueado})
        return bloqueado

    def listar_usuarios(self, id_usuario, tipo, online):
        self.obter_usuario(id_usuario)
        if tipo == "0":
            ids = set(online)
        elif tipo == "1":
            ids = set()
            for amizade in self.banco.listar("Amizade"):
                if amizade["id_usuario_1"] == id_usuario and not amizade["pendente"]:
                    ids.add(amizade["id_usuario_2"])
        else:
            raise ErroNegocio("Tipo de lista inválido")
        return [(usuario["id"], usuario["apelido"])
                for usuario in self.banco.listar("Usuario") if usuario["id"] in ids]

    def verificar_notificacoes(self, id_usuario):
        self.obter_usuario(id_usuario)
        return [amizade["id_usuario_2"] for amizade in self.banco.listar("Amizade")
                if amizade["id_usuario_1"] == id_usuario
                and amizade["ha_notificacao"] and not amizade["bloqueado"]
                and not amizade["pendente"]]

    def enviar_mensagem(self, id_usuario, id_amigo, texto):
        amizade = self.exigir_amizade(id_usuario, id_amigo)
        inversa = self.exigir_amizade(id_amigo, id_usuario)
        texto = validar_texto(texto, "mensagem")
        agora = datetime.now()
        self.banco.inserir("Conversa", [
            amizade["id"], agora.strftime("%d/%m/%Y"), agora.hour, agora.minute, texto,
        ])
        # Guardo o aviso mesmo silenciado, sem perder a mensagem
        self.banco.atualizar("Amizade", inversa["id"], {"ha_notificacao": True})

    def pegar_historico(self, id_usuario, id_amigo):
        amizade = self.exigir_amizade(id_usuario, id_amigo)
        inversa = self.exigir_amizade(id_amigo, id_usuario)
        origens = {amizade["id"]: id_usuario, inversa["id"]: id_amigo}
        mensagens = []
        for conversa in self.banco.listar("Conversa"):
            if conversa["id_amizade"] in origens:
                conversa["remetente"] = origens[conversa["id_amizade"]]
                mensagens.append(conversa)

        # Junto os dois sentidos e uso o ID para desempatar o mesmo minuto
        mensagens.sort(key=lambda m: (
            datetime.strptime(m["data"], "%d/%m/%Y"),
            m["hora"], m["minuto"], m["id"],
        ))
        return mensagens

    def pegar_mensagens(self, id_usuario, id_amigo):
        amizade = self.exigir_amizade(id_usuario, id_amigo)
        historico = self.pegar_historico(id_usuario, id_amigo)
        novas = [m for m in historico if m["id"] > amizade["ultima_leitura"]]
        if novas or amizade["ha_notificacao"]:
            ultimo_id = max((m["id"] for m in historico), default=0)
            self.banco.atualizar("Amizade", amizade["id"], {
                "ultima_leitura": ultimo_id, "ha_notificacao": False,
            })
        return novas
