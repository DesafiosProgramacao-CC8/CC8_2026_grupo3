# Responsável por encontrar as imagens da pasta, criar seus objetos com metadados
# e inseri-las na árvore utilizada para indexação e pesquisa.f
from scanner import buscar_arquivos
from imagens import ImagemArquivo
from arvore_imagens import ArvoreImagens

# Recebe a pasta, indexa as imagens e identifica os documentos TXT
def indexar_arquivos(caminho_pasta):
    arquivos_imagens, arquivos_documentos = buscar_arquivos(caminho_pasta)
    arvore_imagens = ArvoreImagens()

    for arquivo in arquivos_imagens:
        try:
            imagem = ImagemArquivo(arquivo) # cria objeto com os metadados da imagem
            arvore_imagens.inserir(imagem) # insere a imagem na árvore
        except (PermissionError, OSError):
            continue # ignora arquivos que não podem ser acessados

    return arvore_imagens, arquivos_documentos
