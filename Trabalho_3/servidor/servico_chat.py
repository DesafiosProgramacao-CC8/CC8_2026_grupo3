from datetime import datetime
from threading import Lock

from .banco_chat import ARQUIVO_BANCO, BancoChat
from .fila_banco import FilaBanco
from .regras_negocio import ErroNegocio, RegrasNegocio, validar_texto


def criar_resposta(codigo, *campos):
    partes = [str(codigo)] + [str(campo) for campo in campos]
    return "|".join(partes) + "|#\n"


def resposta_mensagens(codigo, mensagens):
    campos = []
    for mensagem in mensagens:
        if codigo == 1025:
            campos.extend([
                mensagem["remetente"], mensagem["mensagem"], mensagem["data"],
                mensagem["hora"], mensagem["minuto"],
            ])
        else:
            # O histórico tem uma ordem diferente no protocolo do professor
            campos.extend([
                mensagem["remetente"], mensagem["data"], mensagem["hora"],
                mensagem["minuto"], mensagem["mensagem"],
            ])
    return criar_resposta(codigo, *campos)


class ServicoChat:
    def __init__(self, gerenciador, caminho=ARQUIVO_BANCO):
        self.gerenciador = gerenciador
        self.banco = BancoChat(caminho)
        self.regras = RegrasNegocio(self.banco)
        self.fila = FilaBanco()
        self.mensagens_gerais = {}
        self.trava_avisos = Lock()

    def executar(self, codigo, parametros, id_conexao):
        # A validação e a alteração ficam juntas dentro da mesma fila
        return self.fila.executar(self._executar, codigo, parametros, id_conexao)

    def _executar(self, codigo, parametros, id_conexao):
        id_usuario = self.gerenciador.obter_usuario(id_conexao)
        if codigo == 8:
            self.banco.executar(self.regras.cadastrar, *parametros)
            return criar_resposta(9)

        if codigo == 16:
            if id_usuario is not None:
                raise ErroNegocio("Esta conexão já está autenticada")
            id_usuario = self.banco.executar(self.regras.autenticar, *parametros)
            if self.gerenciador.usuario_esta_online(id_usuario):
                raise ErroNegocio("Este usuário já está online")
            self.banco.executar(self.regras.preparar_avisos_login, id_usuario)
            if not self.gerenciador.autenticar_conexao(id_conexao, id_usuario):
                raise ErroNegocio("Usuário já está online ou conexão inválida")
            self.mensagens_gerais[id_usuario] = []
            return criar_resposta(17, id_usuario)

        if id_usuario is None:
            raise ErroNegocio("Faça login antes de usar este comando")

        # O ID informado não pode servir para agir no lugar de outra pessoa
        # VERPERFIL é a exceção porque consulta dados públicos de outro usuário
        if codigo != 8192 and int(parametros[0]) != id_usuario:
            raise ErroNegocio("O ID informado não pertence à sua conexão")

        if codigo == 32:
            return criar_resposta(33)

        if codigo == 64:
            usuarios = self.banco.executar(
                self.regras.listar_usuarios, id_usuario, parametros[1],
                self.gerenciador.listar_usuarios_online(),
            )
            campos = []
            for identificador, apelido in usuarios:
                campos.extend([identificador, apelido])
            return criar_resposta(65, *campos)

        if codigo == 128:
            ids = self.banco.executar(self.regras.verificar_notificacoes, id_usuario)
            return criar_resposta(129, *ids)

        if codigo == 256:
            self.banco.executar(self.regras.solicitar_amizade, id_usuario, int(parametros[1]))
            # O código 257 será enviado para quem recebeu o convite
            return None

        if codigo == 258:
            self.banco.executar(
                self.regras.responder_amizade, id_usuario, int(parametros[1]),
                parametros[2] == "VERDADEIRO",
            )
            # O código 259 será enviado para quem fez o convite
            return None

        if codigo == 512:
            self.banco.executar(self.regras.alterar_silenciamento, id_usuario, int(parametros[1]))
            return criar_resposta(513)

        if codigo == 2048:
            if parametros[1] == "":
                texto = validar_texto(parametros[2], "mensagem")
                agora = datetime.now()
                mensagem = {
                    "remetente": id_usuario, "mensagem": texto,
                    "data": agora.strftime("%d/%m/%Y"),
                    "hora": agora.hour, "minuto": agora.minute,
                }
                # Só quem está online no momento recebe a mensagem geral
                for pendentes in self.mensagens_gerais.values():
                    pendentes.append(dict(mensagem))
            else:
                self.banco.executar(
                    self.regras.enviar_mensagem, id_usuario,
                    int(parametros[1]), parametros[2],
                )
            return criar_resposta(2049)

        if codigo == 1024:
            if parametros[1] == "":
                mensagens = self.mensagens_gerais[id_usuario]
                self.mensagens_gerais[id_usuario] = []
            else:
                mensagens = self.banco.executar(
                    self.regras.pegar_mensagens, id_usuario, int(parametros[1]),
                )
            return resposta_mensagens(1025, mensagens)

        if codigo == 4096:
            mensagens = self.banco.executar(
                self.regras.pegar_historico, id_usuario, int(parametros[1]),
            )
            return resposta_mensagens(4097, mensagens)

        if codigo == 8192:
            perfil = self.banco.executar(self.regras.ver_perfil, int(parametros[0]))
            return criar_resposta(8193, perfil["id"], perfil["nome"], perfil["apelido"], perfil["idade"])

        if codigo == 16384:
            self.banco.executar(self.regras.atualizar_perfil, id_usuario, *parametros[1:])
            return criar_resposta(16385)

        raise ErroNegocio("Comando desconhecido")

    def entregar_avisos(self):
        # O envio pela rede acontece fora da fila para não prender o banco
        if not self.trava_avisos.acquire(blocking=False):
            return
        try:
            avisos = self.fila.executar(self.banco.listar, "AvisoAmizade")
            for aviso in avisos:
                campos = [aviso["origem"]]
                if aviso["codigo"] == 259:
                    campos.append(aviso["resposta"])
                mensagem = criar_resposta(aviso["codigo"], *campos)
                if self.gerenciador.enviar_para_usuario(aviso["destinatario"], mensagem):
                    self.fila.executar(
                        self.banco.executar, self.banco.remover, "AvisoAmizade", aviso["id"],
                    )
        finally:
            self.trava_avisos.release()

    def finalizar_conexao(self, id_conexao):
        self.fila.executar(self._finalizar_conexao, id_conexao)

    def _finalizar_conexao(self, id_conexao):
        dados = self.gerenciador.remover_conexao(id_conexao)
        if dados is not None:
            self.mensagens_gerais.pop(dados["id_usuario"], None)

    def fechar(self):
        self.fila.fechar()
