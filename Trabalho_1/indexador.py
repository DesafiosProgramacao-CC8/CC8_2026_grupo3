# Responsável por encontrar os arquivos da pasta, criar seus objetos
# e inseri-los nas árvores utilizadas para indexação e pesquisa.

from scanner import buscar_arquivos
from imagens import ImagemArquivo
from arvore_imagens import ArvoreImagens
from processador_documentos import criar_documento
from arvore_documentos import ArvoreDocumentos


# Recebe a pasta e cria os índices de imagens e documentos
def indexar_arquivos(caminho_pasta):
    arquivos_imagens, arquivos_documentos = buscar_arquivos(caminho_pasta)

    arvore_imagens = ArvoreImagens()
    arvore_documentos = ArvoreDocumentos()

    for arquivo in arquivos_imagens:
        try:
            imagem = ImagemArquivo(arquivo) # cria objeto com os metadados da imagem
            arvore_imagens.inserir(imagem) # insere a imagem na árvore

        except (PermissionError, OSError):
            continue # ignora arquivos que não podem ser acessados

    for arquivo in arquivos_documentos:
        try:
            documento = criar_documento(arquivo) # cria objeto com os dados do documento
            arvore_documentos.inserir(documento) # insere o documento na árvore

        except (PermissionError, OSError):
            continue # ignora arquivos que não podem ser acessados

    return arvore_imagens, arvore_documentos