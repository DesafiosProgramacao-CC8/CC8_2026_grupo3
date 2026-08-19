# Representa cada nó da árvore
class No:
    def __init__(self, imagem):
        # Objeto ImagemArquivo armazenado no nó
        self.imagem = imagem

        # Referências para os filhos esquerdo e direito
        self.esquerda = None
        self.direita = None


# Árvore binária utilizada para indexar as imagens pelo nome
class ArvoreImagens:
    def __init__(self):
        # Inicializa a árvore vazia
        self.raiz = None

    # Insere uma nova imagem na árvore
    def inserir(self, imagem):
        self.raiz = self._inserir(self.raiz, imagem)

    # Realiza a inserção recursivamente
    def _inserir(self, no, imagem):
        # Se a posição estiver vazia, cria um novo nó
        if no is None:
            return No(imagem)

        # Nomes menores alfabeticamente vão para a esquerda
        if imagem.nome.lower() < no.imagem.nome.lower():
            no.esquerda = self._inserir(no.esquerda, imagem)

        # Nomes maiores ou iguais vão para a direita
        else:
            no.direita = self._inserir(no.direita, imagem)

        return no

    # Inicia a busca exata pelo nome
    def buscar_nome(self, nome):
        return self._buscar_nome(self.raiz, nome.lower())

    # Busca o nome recursivamente na árvore
    def _buscar_nome(self, no, nome):
        # Se chegou a uma posição vazia, a imagem não existe
        if no is None:
            return None

        nome_atual = no.imagem.nome.lower()

        # Retorna a imagem caso o nome seja encontrado
        if nome == nome_atual:
            return no.imagem

        # Se o nome procurado for menor, busca à esquerda
        if nome < nome_atual:
            return self._buscar_nome(no.esquerda, nome)

        # Caso contrário, busca à direita
        return self._buscar_nome(no.direita, nome)

    # Retorna todas as imagens armazenadas
    def listar_imagens(self):
        imagens = []
        self._listar(self.raiz, imagens)
        return imagens

    # Percorre a árvore em ordem: esquerda, nó atual, direita
    def _listar(self, no, imagens):
        if no is None:
            return

        self._listar(no.esquerda, imagens)
        imagens.append(no.imagem)
        self._listar(no.direita, imagens)

    # Busca todas as imagens com determinada extensão
    def buscar_extensao(self, extensao):
        resultados = []

        extensao = extensao.lower()

        # Permite pesquisar tanto "png" quanto ".png"
        if not extensao.startswith("."):
            extensao = "." + extensao

        for imagem in self.listar_imagens():
            if imagem.extensao.lower() == extensao:
                resultados.append(imagem)

        return resultados

    # Busca imagens com largura e altura específicas
    def buscar_dimensoes(self, largura, altura):
        resultados = []

        for imagem in self.listar_imagens():
            if (
                imagem.largura == largura
                and imagem.altura == altura
            ):
                resultados.append(imagem)

        return resultados

    # Busca imagens pelo formato real, como PNG ou JPEG
    def buscar_formato(self, formato):
        resultados = []

        formato = formato.lower()

        for imagem in self.listar_imagens():
            if imagem.formato is not None:
                if imagem.formato.lower() == formato:
                    resultados.append(imagem)

        return resultados

    # Busca imagens com tamanho maior ou igual ao valor informado
    def buscar_tamanho_minimo(self, tamanho_minimo):
        resultados = []

        for imagem in self.listar_imagens():
            if imagem.tamanho >= tamanho_minimo:
                resultados.append(imagem)

        return resultados

    # Busca imagens que contenham um termo em qualquer parte do nome
    def buscar_nome_parcial(self, termo):
        resultados = []

        termo = termo.lower()

        for imagem in self.listar_imagens():
            if termo in imagem.nome.lower():
                resultados.append(imagem)

        return resultados

    # Exibe todas as imagens armazenadas na árvore
    def mostrar(self):
        self._mostrar(self.raiz)

    # Percorre e imprime a árvore em ordem
    def _mostrar(self, no):
        if no is None:
            return

        self._mostrar(no.esquerda)
        print(no.imagem)
        self._mostrar(no.direita)