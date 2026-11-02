from queue import Queue
from threading import Lock, Thread, current_thread


class FilaBanco:
    def __init__(self):
        self.fila = Queue()
        self.trava = Lock()
        self.fechada = False
        self.trabalhador = Thread(target=self._atender, daemon=True)
        self.trabalhador.start()

    def executar(self, operacao, *argumentos):
        if current_thread() is self.trabalhador:
            raise RuntimeError("Uma tarefa não pode esperar pela própria fila")

        # Cada pedido tem uma fila pequena para receber seu resultado
        retorno = Queue(maxsize=1)
        with self.trava:
            if self.fechada:
                raise RuntimeError("A fila do banco já foi encerrada")
            self.fila.put((operacao, argumentos, retorno))

        resultado, erro = retorno.get()
        if erro is not None:
            raise erro
        return resultado

    def _atender(self):
        while True:
            pedido = self.fila.get()
            try:
                if pedido is None:
                    return
                operacao, argumentos, retorno = pedido
                try:
                    resultado = operacao(*argumentos)
                    retorno.put((resultado, None))
                except Exception as erro:
                    # Um pedido com erro não impede os próximos de funcionar
                    retorno.put((None, erro))
            finally:
                self.fila.task_done()

    def fechar(self):
        with self.trava:
            if not self.fechada:
                self.fechada = True
                # O aviso de encerramento entra depois dos pedidos já recebidos
                self.fila.put(None)
        self.trabalhador.join()
