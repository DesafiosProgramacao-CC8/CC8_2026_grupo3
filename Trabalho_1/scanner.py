from pathlib import Path

def buscar_arquivos(caminho_pasta):
    pasta = Path(caminho_pasta) # transforma o caminho em um objeto Path

    imagens = [] # armazena os caminhos das imagens encontradas
    documentos = [] # armazena os caminhos dos documentos encontrados

    if not pasta.exists(): # verifica se a pasta existe
        print("A pasta não existe.")
        return imagens, documentos

    if not pasta.is_dir(): # verifica se o caminho informado é uma pasta
        print("O caminho informado não é uma pasta.")
        return imagens, documentos

    try:
        for item in pasta.rglob("*"): # percorre a pasta e suas subpastas
            try:
                if item.is_file(): # verifica se o item é um arquivo

                    extensao = item.suffix.lower()

                    if extensao in [".jpg", ".png"]:
                        imagens.append(item)

                    elif extensao == ".txt":
                        documentos.append(item)

            except PermissionError:
                continue # ignora itens sem permissão e continua

    except PermissionError:
        pass

    return imagens, documentos