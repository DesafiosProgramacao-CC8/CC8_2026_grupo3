import io
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

# O cliente também usa esses imports ao iniciar por cliente/main.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cliente"))

from conexao import ConexaoTCP, ErroConexao, LIMITE_BYTES
from protocolo_cliente import criar_mensagem
from Trabalho_3.servidor.servico_chat import resposta_mensagens


class TesteRespostasChat(unittest.TestCase):
    def setUp(self):
        self.cliente = ConexaoTCP()
        self.cliente._socket = Mock()
        self.cliente.id_usuario = 1
        self.addCleanup(self.cliente._fechar)

    def receber(self, resposta):
        self.cliente._arquivo = io.BytesIO(resposta)

    def mensagens(self, quantidade, texto="x" * 80):
        return [
            {
                "remetente": 1, "mensagem": f"{indice:02d} {texto}",
                "data": "18/11/2026", "hora": 15, "minuto": 30,
            }
            for indice in range(quantidade)
        ]

    def test_historico_com_50_mensagens_nao_desconecta(self):
        mensagens = self.mensagens(50)
        resposta = resposta_mensagens(4097, mensagens).encode("utf-8")
        self.assertGreater(len(resposta), 4096)
        # A resposta seguinte deve continuar disponível para o próximo pedido.
        self.receber(resposta + b"5|#\n")

        codigo, campos = self.cliente.requisitar(4096, 1, "")

        self.assertEqual(codigo, 4097)
        self.assertEqual(campos[4::5], [m["mensagem"] for m in mensagens])
        self.assertTrue(self.cliente.ping())
        self.assertTrue(self.cliente.conectado)

    def test_historico_com_200_mensagens_longas_e_acentos(self):
        mensagens = self.mensagens(200, "ação " * 560)
        for mensagem in mensagens:
            pedido = criar_mensagem(2048, 1, "", mensagem["mensagem"])
            # Completa cada pedido até o máximo aceito pelo servidor, em bytes.
            mensagem["mensagem"] += "x" * (4096 - len(pedido.encode("utf-8")))
            pedido = criar_mensagem(2048, 1, "", mensagem["mensagem"])
            self.assertEqual(len(pedido.encode("utf-8")), 4096)
        self.receber(resposta_mensagens(4097, mensagens).encode("utf-8"))

        codigo, campos = self.cliente.requisitar(4096, 1, "")

        self.assertEqual(codigo, 4097)
        self.assertEqual(campos[4::5], [m["mensagem"] for m in mensagens])
        self.assertTrue(self.cliente.conectado)

    def test_consulta_com_muitas_mensagens_novas(self):
        mensagens = self.mensagens(50)
        self.receber(resposta_mensagens(1025, mensagens).encode("utf-8"))

        codigo, campos = self.cliente.requisitar(1024, 1, "")

        self.assertEqual(codigo, 1025)
        self.assertEqual(campos[1::5], [m["mensagem"] for m in mensagens])

    def test_resposta_exatamente_no_limite_e_aceita(self):
        prefixo = b"4097|1|18/11/2026|15|30|"
        sufixo = b"|#\n"
        tamanho_texto = LIMITE_BYTES - len(prefixo) - len(sufixo)
        self.receber(prefixo + b"x" * tamanho_texto + sufixo)

        codigo, campos = self.cliente.requisitar(4096, 1, "")

        self.assertEqual(codigo, 4097)
        self.assertEqual(len(campos[4]), tamanho_texto)

    def test_resposta_acima_do_limite_fecha_conexao(self):
        self.receber(b"x" * (LIMITE_BYTES + 1))

        with self.assertRaisesRegex(ErroConexao, "resposta muito longa"):
            self.cliente.requisitar(4096, 1, "")

        self.assertFalse(self.cliente.conectado)
        self.assertIsNone(self.cliente.id_usuario)

    def test_conexao_encerrada_pelo_servidor(self):
        self.receber(b"")

        with self.assertRaises(ErroConexao):
            self.cliente.requisitar(4096, 1, "")

        self.assertFalse(self.cliente.conectado)

    def test_resposta_sem_terminador_e_rejeitada(self):
        self.receber(b"4097|1|18/11/2026|15|30|incompleta")

        with self.assertRaisesRegex(ErroConexao, "sem terminador"):
            self.cliente.requisitar(4096, 1, "")

    def test_ping_preserva_aviso_recebido_antes_da_resposta(self):
        self.receber(b"257|2|#\n5|#\n")

        self.assertTrue(self.cliente.ping())
        self.assertEqual(self.cliente.retirar_avisos(), [(257, ["2"])])


if __name__ == "__main__":
    unittest.main()
