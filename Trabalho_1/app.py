import os
import subprocess
import sys
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for

from indexador import indexar_arquivos
from processador_documentos import buscar_documentos


# Cria a aplicação Web local usando Flask
app = Flask(__name__)
app.secret_key = "iffagle-local" # chave usada para exibir mensagens na tela

# Guarda em memória a pasta escolhida e as árvores geradas na indexação
estado = {"pasta": None, "imagens": None, "documentos": None}


# Verifica se uma pasta já foi indexada
def indexado():
    return all(valor is not None for valor in estado.values())


# Renderiza a página principal com os dados atuais
def pagina(resultados=None, termo="", tipo="todos"):
    return render_template(
        "index.html",
        pasta=estado["pasta"],
        termo=termo,
        tipo=tipo,
        resultados=resultados,
    )


# Monta o dicionário de um documento para exibir no HTML
def item_doc(doc, relevancia=None):
    return {
        "tipo": "documento",
        "nome": doc.nome,
        "caminho": str(doc.caminho),
        "tamanho": doc.tamanho,
        "quantidade_palavras": doc.quantidade_palavras,
        "relevancia": relevancia,
    }


# Monta o dicionário de uma imagem para exibir no HTML
def item_img(img):
    return {
        "tipo": "imagem",
        "nome": img.nome,
        "caminho": img.caminho,
        "extensao": img.extensao,
        "tamanho": img.tamanho,
        "largura": img.largura,
        "altura": img.altura,
        "formato": img.formato,
    }


# Busca documentos e imagens respeitando o filtro escolhido
def buscar(termo, tipo):
    docs = estado["documentos"].listar_documentos() # lista documentos da árvore
    imgs = estado["imagens"].listar_imagens() # lista imagens da árvore
    resultados = [] # guarda todos os resultados que serão mostrados

    # Busca documentos quando o filtro permite
    if tipo in ("todos", "documentos"):
        if termo:
            resultados += [item_doc(doc, rel) for doc, rel in buscar_documentos(docs, termo)]
        else:
            resultados += [item_doc(doc) for doc in docs]

    # Busca imagens quando o filtro permite
    if tipo in ("todos", "imagens"):
        if termo:
            imgs = estado["imagens"].buscar_nome_parcial(termo)
        resultados += [item_img(img) for img in imgs]

    return resultados


# Confere se o arquivo pertence à pasta indexada antes de abrir ou visualizar
def arquivo_indexado(caminho):
    if not indexado():
        abort(400)

    raiz = Path(estado["pasta"]).resolve() # caminho da pasta indexada
    arquivo = Path(caminho).resolve() # caminho do arquivo recebido pela página

    if raiz not in arquivo.parents or not arquivo.is_file():
        abort(404)

    return arquivo


# Indexa a pasta escolhida pelo usuário
def carregar_pasta(pasta):
    if not pasta.is_dir():
        return "Informe uma pasta válida."

    try:
        estado["imagens"], estado["documentos"] = indexar_arquivos(pasta) # cria as árvores
        estado["pasta"] = str(pasta.resolve()) # salva o caminho absoluto
    except Exception as erro:
        return f"Não foi possível indexar a pasta: {erro}"

    return None


@app.route("/", methods=["GET", "POST"])
def inicio():
    # Recebe o caminho digitado manualmente
    if request.method == "POST":
        pasta = Path(request.form.get("pasta", "").strip().strip('"')).expanduser()
        erro = carregar_pasta(pasta)
        if erro:
            flash(erro)

        return redirect(url_for("inicio"))

    # Se não existe busca, mostra apenas a tela inicial
    termo = request.args.get("termo")
    if termo is None:
        return pagina()

    # Impede buscar antes da indexação
    if not indexado():
        flash("Informe uma pasta antes de buscar.")
        return redirect(url_for("inicio"))

    termo = termo.strip().lower() # normaliza o termo pesquisado
    tipo = request.args.get("tipo", "todos") # lê o filtro de tipo de arquivo
    if tipo not in ("todos", "imagens", "documentos"):
        tipo = "todos"

    return pagina(buscar(termo, tipo), termo, tipo)


@app.route("/selecionar-pasta", methods=["POST"])
def selecionar_pasta():
    try:
        # Abre o seletor visual de pastas do sistema operacional
        import tkinter as tk
        from tkinter import filedialog

        janela = tk.Tk() # cria uma janela base para o seletor
        janela.withdraw() # esconde a janela base
        janela.attributes("-topmost", True) # tenta manter o seletor na frente
        janela.update() # atualiza a janela antes de abrir o seletor
        caminho = filedialog.askdirectory(parent=janela, title="Escolha a pasta")
        janela.destroy()
    except Exception as erro:
        flash(f"Não foi possível abrir o seletor: {erro}")
        return redirect(url_for("inicio"))

    # Indexa a pasta selecionada se o usuário não cancelar
    if caminho:
        erro = carregar_pasta(Path(caminho))
        if erro:
            flash(erro)
    else:
        flash("Nenhuma pasta selecionada.")

    return redirect(url_for("inicio"))


@app.route("/preview")
def preview():
    # Envia a imagem para pré-visualização no navegador
    return send_file(arquivo_indexado(request.args.get("caminho", "")))


@app.route("/abrir", methods=["POST"])
def abrir():
    arquivo = str(arquivo_indexado(request.form.get("caminho", "")))

    # Abre o arquivo com o comando correto para cada sistema operacional
    if os.name == "nt":
        os.startfile(arquivo)
    elif sys.platform == "darwin":
        subprocess.run(["open", arquivo], check=False)
    else:
        subprocess.run(["xdg-open", arquivo], check=False)

    return redirect(request.referrer or url_for("inicio"))


if __name__ == "__main__":
    # threaded=False evita conflito entre Flask e tkinter no seletor de pasta
    app.run(debug=True, port=5000, use_reloader=False, threaded=False)
