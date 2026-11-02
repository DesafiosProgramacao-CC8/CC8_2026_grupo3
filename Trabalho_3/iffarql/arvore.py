class No:
    def __init__(self, id, registro):
        self.id = id
        self.registro = registro

        self.esquerda = None
        self.direita = None


class ArvoreRegistros:
    def __init__(self):
        self.raiz = None

    def inserir(self, id, registro):
        self.raiz = self._inserir(
            self.raiz,
            id,
            registro
        )

    def _inserir(self, no, id, registro):

        if no is None:
            return No(id, registro)

        if id < no.id:
            no.esquerda = self._inserir(
                no.esquerda,
                id,
                registro
            )

        elif id > no.id:
            no.direita = self._inserir(
                no.direita,
                id,
                registro
            )

        else:
            raise Exception("ID já existente")

        return no

    def buscar(self, id):
        return self._buscar(
            self.raiz,
            id
        )

    def _buscar(self, no, id):

        if no is None:
            return None

        if id == no.id:
            return no.registro

        if id < no.id:
            return self._buscar(
                no.esquerda,
                id
            )

        return self._buscar(
            no.direita,
            id
        )

    def esta_vazia(self):
        return self.raiz is None

    def listar_registros(self):
        registros = []

        self._listar(
            self.raiz,
            registros
        )

        return registros

    def _listar(self, no, registros):

        if no is None:
            return

        self._listar(
            no.esquerda,
            registros
        )

        registros.append(no.registro)

        self._listar(
            no.direita,
            registros
        )

    def remover(self, id):
        self.raiz = self._remover(self.raiz, id)


    def _remover(self, no, id):

        if no is None:
            return None

        if id < no.id:
            no.esquerda = self._remover(no.esquerda, id)

        elif id > no.id:
            no.direita = self._remover(no.direita, id)

        else:

            if no.esquerda is None:
                return no.direita

            if no.direita is None:
                return no.esquerda

            sucessor = self._menor_no(no.direita)

            no.id = sucessor.id
            no.registro = sucessor.registro

            no.direita = self._remover(
                no.direita,
                sucessor.id
            )

        return no


    def _menor_no(self, no):

        atual = no

        while atual.esquerda is not None:
            atual = atual.esquerda

        return atual