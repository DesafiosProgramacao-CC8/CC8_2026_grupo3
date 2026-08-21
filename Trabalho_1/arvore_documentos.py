# Representa cada nó da árvore
class No:
    def __init__(self, documento):
        # Objeto DocumentoArquivo armazenado no nó
        self.documento = documento

        # Referências para os filhos esquerdo e direito
        self.esquerda = None
        self.direita = None


# Árvore binária utilizada para indexar os documentos pelo nome
class ArvoreDocumentos:
    def __init__(self):
        # Inicializa a árvore vazia
        self.raiz = None

    # Insere um novo documento na árvore
    def inserir(self, documento):
        self.raiz = self._inserir(self.raiz, documento)

    # Realiza a inserção recursivamente
    def _inserir(self, no, documento):
        # Se a posição estiver vazia, cria um novo nó
        if no is None:
            return No(documento)

        # Nomes menores alfabeticamente vão para a esquerda
        if documento.nome.lower() < no.documento.nome.lower():
            no.esquerda = self._inserir(no.esquerda, documento)

        # Nomes maiores ou iguais vão para a direita
        else:
            no.direita = self._inserir(no.direita, documento)

        return no

    # Inicia a busca exata pelo nome
    def buscar_nome(self, nome):
        nome = nome.lower()

        # Permite pesquisar tanto "texto1" quanto "texto1.txt"
        if not nome.endswith(".txt"):
            nome = nome + ".txt"

        return self._buscar_nome(self.raiz, nome)

    # Busca o nome recursivamente na árvore
    def _buscar_nome(self, no, nome):
        # Se chegou a uma posição vazia, o documento não existe
        if no is None:
            return None

        nome_atual = no.documento.nome.lower()

        # Retorna o documento caso o nome seja encontrado
        if nome == nome_atual:
            return no.documento

        # Se o nome procurado for menor, busca à esquerda
        if nome < nome_atual:
            return self._buscar_nome(no.esquerda, nome)

        # Caso contrário, busca à direita
        return self._buscar_nome(no.direita, nome)

    # Retorna todos os documentos armazenados
    def listar_documentos(self):
        documentos = []
        self._listar(self.raiz, documentos)
        return documentos

    # Percorre a árvore em ordem: esquerda, nó atual, direita
    def _listar(self, no, documentos):
        if no is None:
            return

        self._listar(no.esquerda, documentos)
        documentos.append(no.documento)
        self._listar(no.direita, documentos)

    # Busca documentos com tamanho maior ou igual ao valor informado
    def buscar_tamanho_minimo(self, tamanho_minimo):
        resultados = []

        for documento in self.listar_documentos():
            if documento.tamanho >= tamanho_minimo:
                resultados.append(documento)

        return resultados

    # Busca documentos que contenham um termo em qualquer parte do nome
    def buscar_nome_parcial(self, termo):
        resultados = []

        termo = termo.lower()

        for documento in self.listar_documentos():
            if termo in documento.nome.lower():
                resultados.append(documento)

        return resultados

    # Exibe todos os documentos armazenados na árvore
    def mostrar(self):
        self._mostrar(self.raiz)

    # Percorre e imprime a árvore em ordem
    def _mostrar(self, no):
        if no is None:
            return

        self._mostrar(no.esquerda)
        print(no.documento)
        self._mostrar(no.direita)