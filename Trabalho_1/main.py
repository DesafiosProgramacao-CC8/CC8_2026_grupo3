from indexador import indexar_arquivos
from documentos import buscar_documentos


pasta = input("Digite o caminho da pasta: ")

arvore_imagens, documentos = indexar_arquivos(pasta)

print("\nIndexação concluída!")


while True:
    print("\n1 - Buscar imagem por nome")
    print("2 - Buscar imagem por extensão")
    print("3 - Buscar imagem por dimensões")
    print("4 - Listar todas as imagens")
    print("5 - Buscar documentos por conteúdo")
    print("6 - Listar documentos encontrados")
    print("0 - Sair")

    opcao = input("\nEscolha: ")

    if opcao == "1":
        nome = input("Nome da imagem: ")
        resultado = arvore_imagens.buscar_nome(nome)

        if resultado:
            print(resultado)
            print("Caminho:", resultado.caminho)
        else:
            print("Imagem não encontrada.")

    elif opcao == "2":
        extensao = input("Extensão (.jpg ou .png): ")
        resultados = arvore_imagens.buscar_extensao(extensao)

        for imagem in resultados:
            print(imagem)

    elif opcao == "3":
        largura = int(input("Largura: "))
        altura = int(input("Altura: "))

        resultados = arvore_imagens.buscar_dimensoes(
            largura,
            altura
        )

        for imagem in resultados:
            print(imagem)

    elif opcao == "4":
        for imagem in arvore_imagens.listar_imagens():
            print(imagem)

    elif opcao == "5":
        termo = input("Digite uma palavra para pesquisar: ")

        resultados = buscar_documentos(documentos, termo)

        print("\nResultados da busca:")

        if len(resultados) == 0:
            print("Termo '" + termo + "' não encontrado em nenhum documento.")
        else:
            for nome, relevancia in resultados:
                print(nome, "- relevância:", relevancia)

    elif opcao == "6":
        if len(documentos) == 0:
            print("Nenhum documento .txt encontrado.")
        else:
            print("\nDocumentos encontrados:")

            for documento in documentos:
                print(documento)

    elif opcao == "0":
        break