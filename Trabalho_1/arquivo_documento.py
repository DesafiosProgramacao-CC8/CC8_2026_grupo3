class DocumentoArquivo:
    def __init__(self, caminho, frequencia):
        self.caminho = caminho #armazena o caminho do arquivo
        self.nome = caminho.name #armazena o nome do arquivo
        self.extensao = caminho.suffix.lower() #armazena a extensão do arquivo
        self.tamanho = caminho.stat().st_size #armazena o tamanho do arquivo em bytes
        self.frequencia = frequencia #armazena a frequência das palavras do documento

    def __str__(self):
        return self.nome 