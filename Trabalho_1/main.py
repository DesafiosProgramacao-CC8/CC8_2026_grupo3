from indexador import indexar_imagens

pasta = input("Digite o caminho da pasta: ")

arvore = indexar_imagens(pasta)

print("\nIndexação concluída!")

while True:

    print("\n1 - Buscar por nome")
    print("2 - Buscar por extensão")
    print("3 - Buscar por dimensões")
    print("4 - Listar todas")
    print("0 - Sair")

    opcao = input("\nEscolha: ")

    if opcao == "1":
        nome = input("Nome da imagem: ")
        resultado = arvore.buscar_nome(nome)
        if resultado:
            print(resultado)
            print("Caminho:", resultado.caminho)
        else:
            print("Imagem não encontrada.")
    elif opcao == "2":
        extensao = input("Extensão (.jpg ou .png): ")
        resultados = arvore.buscar_extensao(extensao)
        for imagem in resultados:
            print(imagem)
    elif opcao == "3":
        largura = int(input("Largura: "))
        altura = int(input("Altura: "))
        resultados = arvore.buscar_dimensoes(
            largura,
            altura
        )
        for imagem in resultados:
            print(imagem)
    elif opcao == "4":
        for imagem in arvore.listar_imagens():
            print(imagem)
    elif opcao == "0":
        break