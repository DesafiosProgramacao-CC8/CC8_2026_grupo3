# Responsável por encontrar as imagens da pasta, criar seus objetos com metadados
# e inseri-las na árvore utilizada para indexação e pesquisa.f
from scanner import buscar_imagens
from imagens import ImagemArquivo
from arvore_imagens import ArvoreImagens

# Cria o índice de imagens a partir da pasta informada
def indexar_imagens(caminho_pasta): 
    arquivos = buscar_imagens(caminho_pasta)
    arvore = ArvoreImagens()
    for arquivo in arquivos:
        try:
            imagem = ImagemArquivo(arquivo)

            arvore.inserir(imagem)

        except (PermissionError, OSError):
            continue

    return arvore