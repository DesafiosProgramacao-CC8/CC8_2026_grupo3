from pathlib import Path
import string

def encontrar_documentos(pasta):
    documentos = [] #lista que armazena os arquivos .txt encontrados

    for caminho in pasta.rglob("*.txt"): # procura arquivos .txt
        documentos.append(caminho) # adiciona o caminho encontrado à lista
    return documentos 

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

def calcular_relevancia(frequencia, termo):
    termo = termo.lower()

    if termo in frequencia:
        return frequencia[termo]
    else:
        return 0

pasta = Path(__file__).parent / "arquivos_de_teste" #pasta a ser pesquisada
documentos = encontrar_documentos(pasta) # encontra todos os documentos .txt da pasta 

termo = input("Digite uma palavra para pesquisar: ") #palavra chave da busca

resultados = [] #armazena os resultados da busca por meio do nome e relevancia

for documento in documentos:
    conteudo = ler_documento(documento) #lê o conteúdo do documento
    palavras = tratar_texto(conteudo) #trata e separa o conteúdo em palavras
    frequencia = contar_palavras(palavras) #conta a frequência das palavras
    relevancia = calcular_relevancia(frequencia, termo) #calcula a relevância do documento
    if relevancia > 0: # adiciona apenas documentos que possuem o termo pesquisado
        resultados.append(
            (documento.name, relevancia)
    )

resultados.sort( #ordena os resultados pela relevância, do maior para o menor
    key=lambda resultado: resultado[1],
    reverse=True
)

print()
print("Resultados da busca:")

if len(resultados) == 0:
    print("Termo '" + termo + "' não encontrado em nenhum documento.")
else:
    for nome, relevancia in resultados:
        print(nome, "- relevância:", relevancia)