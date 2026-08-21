import string

from arquivo_documento import DocumentoArquivo


def ler_documento(caminho):
    arquivo = open(caminho, "r", encoding="utf-8")
    conteudo = arquivo.read()
    arquivo.close()

    return conteudo


def tratar_texto(conteudo):
    conteudo_minusculo = conteudo.lower() #padroniza o texto para minúsculo
    conteudo_limpo = conteudo_minusculo.translate( #remover pontuação
        str.maketrans("", "", string.punctuation)
    )
    palavras = conteudo_limpo.split() #separa o texto em palavras dentro de uma lista

    return palavras


def contar_palavras(palavras):
    frequencia = {} #dicionário para armazenar a frequência de cada palavra

    for palavra in palavras: #itera sobre cada palavra no conteúdo do documento
        if palavra in frequencia: # verifica se a palavra já está no dicionário
            frequencia[palavra] += 1 #incrementa a contagem da palavra
        else:
            frequencia[palavra] = 1 #adiciona a palavra ao dicionário com contagem 1

    return frequencia


def criar_documento(caminho):
    conteudo = ler_documento(caminho)
    palavras = tratar_texto(conteudo)
    frequencia = contar_palavras(palavras)

    documento = DocumentoArquivo(
        caminho,
        frequencia
    )

    return documento


def calcular_relevancia(frequencia, termo):
    termo = termo.lower()

    if termo in frequencia:
        return frequencia[termo]
    else:
        return 0


def buscar_documentos(documentos, termo):
    resultados = [] #armazena os resultados da busca por meio do documento e relevancia

    for documento in documentos:
        relevancia = calcular_relevancia(
            documento.frequencia,
            termo
        ) #calcula a relevância do documento

        if relevancia > 0: # adiciona apenas documentos que possuem o termo pesquisado
            resultados.append(
                (documento, relevancia)
            )

    resultados.sort( #ordena os resultados pela relevância, do maior para o menor
        key=lambda resultado: resultado[1],
        reverse=True
    )

    return resultados