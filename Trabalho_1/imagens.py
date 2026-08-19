from PIL import Image # Importa Image da biblioteca Pillow para ler metadados das imagens

class ImagemArquivo:

    def __init__(self, caminho):
        self.caminho = str(caminho) #armazena o caminho da imagem como string
        self.nome = caminho.name
        self.extensao = caminho.suffix.lower()
        self.tamanho = caminho.stat().st_size # Obtém e armazena o tamanho do arquivo em bytes

        self.largura = None
        self.altura = None
        self.formato = None

        self.carregar_metadados() # Carrega largura, altura e formato da imagem

    def carregar_metadados(self):
        try:
            with Image.open(self.caminho) as imagem: # Abre a imagem e garante que o arquivo seja fechado após a leitura
                self.largura, self.altura = imagem.size
                self.formato = imagem.format

        except (PermissionError, OSError): # Ignora imagens que não possam ser abertas ou acessadas
            pass

    # Define como as informações da imagem serão emostradas
    def __str__(self):
        return (
            f"{self.nome} | "
            f"{self.extensao} | "
            f"{self.tamanho} bytes | "
            f"{self.largura}x{self.altura}"
        )