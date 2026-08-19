from pathlib import Path

# Busca imagens dentro da pasta informada e de suas subpastas
def buscar_imagens(caminho_pasta):
    pasta = Path(caminho_pasta) #de string vira objeto
    imagens = [] #para armazenar os caminhos das imagens encontradas

    if not pasta.exists(): #verifica se a pasta não existe
        print("A pasta não existe.")
        return imagens

    if not pasta.is_dir(): #verifica se o caminho informado é uma pasta
        print("O caminho informado não é uma pasta.")
        return imagens

    try: 
        for item in pasta.rglob("*"): # Percorre todos os itens da pasta e de suas subpastas
            try: # usado para ignorar erros de permissão ao acessar arquivos ou pastas
                if item.is_file(): # Verifica se o item encontrado é um arquivo
                    if item.suffix.lower() in [".jpg", ".png"]: # Verifica se o arquivo possui uma das extensões de imagem aceitas
                        imagens.append(item)
            
            except PermissionError: # Caso o item não tenha permissão de acesso, ignora e continua a busca
                continue

    except PermissionError: # Caso o item não tenha permissão de acesso, ignora e continua a busca
        pass

    return imagens