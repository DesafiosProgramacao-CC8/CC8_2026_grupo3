from indexador import indexar_arquivos
from processador_documentos import buscar_documentos


pasta = input("Digite o caminho da pasta: ")

arvore_imagens, arvore_documentos = indexar_arquivos(pasta)

print("\nIndexação concluída!")


while True:
    print("\n1 - Buscar imagem por nome")
    print("2 - Buscar imagem por extensão")
    print("3 - Buscar imagem por dimensões")
    print("4 - Listar todas as imagens")
    print("5 - Buscar documento por nome")
    print("6 - Buscar documentos por conteúdo")
    print("7 - Listar todos os documentos")
    print("8 - Ver informações de um documento")
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

        if len(resultados) == 0:
            print("Nenhuma imagem encontrada.")
        else:
            for imagem in resultados:
                print(imagem)

    elif opcao == "3":
        largura = int(input("Largura: "))
        altura = int(input("Altura: "))

        resultados = arvore_imagens.buscar_dimensoes(
            largura,
            altura
        )

        if len(resultados) == 0:
            print("Nenhuma imagem encontrada.")
        else:
            for imagem in resultados:
                print(imagem)

    elif opcao == "4":
        imagens = arvore_imagens.listar_imagens()

        if len(imagens) == 0:
            print("Nenhuma imagem encontrada.")
        else:
            for imagem in imagens:
                print(imagem)

    elif opcao == "5":
        nome = input("Nome do documento: ")

        resultado = arvore_documentos.buscar_nome(nome)

        if resultado:
            print("Nome:", resultado.nome)
            print("Caminho:", resultado.caminho)
        else:
            print("Documento não encontrado.")

    elif opcao == "6":
        termo = input("Digite uma palavra para pesquisar: ")

        documentos = arvore_documentos.listar_documentos()

        resultados = buscar_documentos(
            documentos,
            termo
        )

        print("\nResultados da busca:")

        if len(resultados) == 0:
            print("Termo '" + termo + "' não encontrado em nenhum documento.")
        else:
            for documento, relevancia in resultados:
                print(
                    documento.nome,
                    "- relevância:",
                    relevancia
                )

    elif opcao == "7":
        documentos = arvore_documentos.listar_documentos()

        if len(documentos) == 0:
            print("Nenhum documento .txt encontrado.")
        else:
            print("\nDocumentos encontrados:")

            for documento in documentos:
                print(documento)

    elif opcao == "8":
        nome = input("Nome do documento: ")

        documento = arvore_documentos.buscar_nome(nome)

        if documento:
            print("\nInformações do documento:")
            print("Nome:", documento.nome)
            print("Caminho:", documento.caminho)
            print("Extensão:", documento.extensao)
            print("Tamanho:", documento.tamanho, "bytes")
            print("Total de palavras:", documento.quantidade_palavras)
            print("Palavras diferentes:", len(documento.frequencia))
        else:
            print("Documento não encontrado.")

    elif opcao == "0":
        break

    else:
        print("Opção inválida.")