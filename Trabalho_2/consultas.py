from condicoes import avaliar_condicao

# Mostra um registro com todos os seus campos, incluindo o id.
def exibir_registro(registro):
    print(registro.valores)

# Mostra os registros de uma tabela, podendo aplicar uma condição ONDE.
def mostrar_dados(banco, nome_tabela, nome_coluna=None, operador=None, token=None):
    tabela = banco.buscar_tabela(nome_tabela)
    registros = tabela.arvore.listar_registros()
    registros_encontrados = 0

    for registro in registros:
        # Sem ONDE, todos os registros devem ser mostrados.
        if nome_coluna is None:
            exibir_registro(registro)
            registros_encontrados += 1

        # Com ONDE, mostra somente os registros que atendem à condição.
        else:
            atende_condicao = avaliar_condicao(
                tabela,
                registro,
                nome_coluna,
                operador,
                token
            )

            if atende_condicao:
                exibir_registro(registro)
                registros_encontrados += 1
    if registros_encontrados == 0:
        print("Nenhum registro encontrado.")

# Remove registros de uma tabela, podendo aplicar uma condição ONDE.
def apagar_dados(
    banco,
    nome_tabela,
    nome_coluna=None,
    operador=None,
    token=None
):
    tabela = banco.buscar_tabela(nome_tabela)

    registros = tabela.arvore.listar_registros()

    ids_para_remover = []

    for registro in registros:

        # Sem ONDE, todos os registros são selecionados para remoção.
        if nome_coluna is None:
            ids_para_remover.append(registro.id)

        # Com ONDE, seleciona somente os registros que atendem à condição.
        else:
            atende_condicao = avaliar_condicao(
                tabela,
                registro,
                nome_coluna,
                operador,
                token
            )

            if atende_condicao:
                ids_para_remover.append(registro.id)

    # Remove da árvore somente depois de finalizar a seleção dos registros.
    for id_registro in ids_para_remover:
        tabela.arvore.remover(id_registro)

    return len(ids_para_remover)